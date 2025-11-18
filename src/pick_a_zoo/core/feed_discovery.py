"""Feed discovery library for detecting URLs and extracting streams.

This module follows the library-first architecture principle and is independently testable.
"""

import re
from enum import Enum
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from loguru import logger
from pydantic import BaseModel, Field

try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    sync_playwright = None  # type: ignore[assignment]
    # Use Exception as fallback when Playwright is unavailable
    PlaywrightTimeoutError = Exception  # type: ignore[assignment, misc]


def _get_browser_headers(url: str | None = None) -> dict[str, str]:
    """Get browser-like HTTP headers to avoid bot detection.

    Args:
        url: Optional URL to set Referer header based on domain

    Returns:
        Dictionary of HTTP headers that mimic a real browser
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,"
            "image/avif,image/webp,image/apng,*/*;q=0.8,"
            "application/signed-exchange;v=b3;q=0.7"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    # Set Referer if URL provided
    if url:
        try:
            parsed = urlparse(url)
            headers["Referer"] = f"{parsed.scheme}://{parsed.netloc}/"
        except Exception:
            pass  # If parsing fails, skip Referer

    return headers


def fetch_html_with_playwright(url: str, timeout: float = 30.0) -> str:
    """Fetch HTML content using Playwright (headless browser).

    This function uses Playwright to load the page, execute JavaScript,
    and return the rendered HTML. Useful for sites with bot protection
    or JavaScript-rendered content.

    Args:
        url: URL to fetch
        timeout: Timeout in seconds (default: 30.0)

    Returns:
        HTML content string after JavaScript execution

    Raises:
        FeedDiscoveryError: If Playwright is not available or fetch fails
    """
    if not PLAYWRIGHT_AVAILABLE or sync_playwright is None:
        raise FeedDiscoveryError(
            "Playwright is not installed. Install it with: playwright install",
            (
                "Browser automation is not available. "
                "Please install Playwright or use a direct stream URL."
            ),
        )

    logger.info(f"Fetching HTML with Playwright: {url}")

    try:
        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ),
            )
            page = context.new_page()

            # Navigate to URL and wait for network to be idle
            try:
                page.goto(url, wait_until="networkidle", timeout=int(timeout * 1000))
            except PlaywrightTimeoutError:
                # If networkidle times out, try with domcontentloaded
                logger.warning("Network idle timeout, trying domcontentloaded")
                page.goto(url, wait_until="domcontentloaded", timeout=int(timeout * 1000))

            # Wait a bit for any delayed JavaScript to execute
            page.wait_for_timeout(2000)  # 2 seconds

            # Get the rendered HTML
            html_content = page.content()

            browser.close()

            logger.info(f"Successfully fetched HTML with Playwright ({len(html_content)} bytes)")
            return html_content

    except PlaywrightTimeoutError as e:
        logger.error(f"Playwright timeout fetching {url}: {e}")
        raise FeedDiscoveryError(
            f"Timeout while fetching page with browser: {url}",
            "The page took too long to load. Please check your connection and try again.",
        ) from e
    except Exception as e:
        logger.error(f"Playwright error fetching {url}: {e}")
        raise FeedDiscoveryError(
            f"Error fetching page with browser: {e}",
            f"Failed to load page: {e}. Please try a direct stream URL instead.",
        ) from e


class URLType(Enum):
    """Enumeration of URL types."""

    DIRECT_STREAM = "direct_stream"
    HTML_PAGE = "html_page"


class StreamCandidate(BaseModel):
    """Represents a candidate stream URL extracted from HTML."""

    url: str = Field(description="Extracted stream URL")
    source_type: str = Field(
        description=("How it was found (e.g., 'video_tag', 'source_tag', " "'m3u8_link', 'iframe')")
    )


class URLValidationResult(BaseModel):
    """Represents the result of validating a URL's accessibility."""

    is_accessible: bool = Field(description="Whether URL is accessible")
    status_code: int | None = Field(default=None, description="HTTP status code if available")
    error_message: str | None = Field(
        default=None, description="Error message if validation failed"
    )
    content_type: str | None = Field(default=None, description="Content-Type header if available")


class FeedDiscoveryError(Exception):
    """Base exception for feed discovery errors."""

    def __init__(self, message: str, user_message: str | None = None):
        """Initialize exception with technical and user-friendly messages.

        Args:
            message: Technical error message for logging
            user_message: User-friendly error message (defaults to message if not provided)
        """
        super().__init__(message)
        self.user_message = user_message or message


class HTMLParseError(FeedDiscoveryError):
    """Exception raised when HTML parsing fails."""

    pass


class URLValidationError(FeedDiscoveryError):
    """Exception raised when URL validation fails."""

    pass


def detect_url_type(url: str) -> URLType:
    """Detect whether URL is a direct stream or HTML page.

    Uses pattern matching first (fast), then falls back to HTTP HEAD request
    to check Content-Type header. Handles redirects up to 5 levels.

    Args:
        url: URL string to analyze

    Returns:
        URLType enum indicating DIRECT_STREAM or HTML_PAGE

    Raises:
        FeedDiscoveryError: If detection fails (network error, etc.)
    """
    logger.debug(f"Detecting URL type for: {url}")

    # Pattern matching for direct streams (fast path)
    direct_stream_patterns = [
        r"\.m3u8$",
        r"\.mp4$",
        r"\.webm$",
        r"\.mkv$",
        r"\.flv$",
        r"rtsp://",
        r"rtmp://",
    ]

    for pattern in direct_stream_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            logger.debug(f"URL matched direct stream pattern: {pattern}")
            return URLType.DIRECT_STREAM

    # HTTP HEAD request fallback for Content-Type checking
    try:
        headers = _get_browser_headers(url)
        with httpx.Client(follow_redirects=True, timeout=15.0, headers=headers) as client:
            response = client.head(url, follow_redirects=True)
            # httpx handles redirects automatically, but we track them manually for logging
            redirect_count = len(response.history)
            if redirect_count > 5:
                logger.warning(f"URL exceeded 5 redirects: {redirect_count}")
                raise FeedDiscoveryError(
                    f"URL exceeded maximum redirect limit (5): {url}",
                    "URL redirects too many times. Please check the URL.",
                )

            content_type = response.headers.get("Content-Type", "").lower()
            logger.debug(f"Content-Type: {content_type}")

            # Check if Content-Type indicates HTML
            if "text/html" in content_type:
                logger.debug("URL detected as HTML page via Content-Type")
                return URLType.HTML_PAGE

            # Check if Content-Type indicates video stream
            if any(
                content_type.startswith(prefix)
                for prefix in ["video/", "application/vnd.apple.mpegurl", "application/x-mpegurl"]
            ):
                logger.debug("URL detected as direct stream via Content-Type")
                return URLType.DIRECT_STREAM

            # Default to HTML_PAGE if Content-Type is ambiguous
            logger.debug("URL defaulting to HTML_PAGE (ambiguous Content-Type)")
            return URLType.HTML_PAGE

    except httpx.TimeoutException as e:
        logger.error(f"Timeout detecting URL type: {e}")
        raise URLValidationError(
            f"Timeout while detecting URL type: {url}",
            "The URL took too long to respond. Please check your connection and try again.",
        ) from e
    except httpx.NetworkError as e:
        logger.error(f"Network error detecting URL type: {e}")
        raise URLValidationError(
            f"Network error while detecting URL type: {url}",
            "Unable to connect to the URL. Please check your internet connection and try again.",
        ) from e
    except httpx.HTTPError as e:
        logger.error(f"HTTP error detecting URL type: {e}")
        raise FeedDiscoveryError(
            f"HTTP error while detecting URL type: {url}",
            f"Unable to access the URL: {e}",
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error detecting URL type: {e}", exc_info=True)
        raise FeedDiscoveryError(
            f"Unexpected error detecting URL type: {url}",
            "An unexpected error occurred. Please try again.",
        ) from e


def extract_streams_from_html(html_content: str, base_url: str) -> list[StreamCandidate]:
    """Extract stream URLs from HTML content.

    Extracts from:
    - <video> tags (src attribute and <source> children)
    - <source> tags (src and srcset attributes)
    - m3u8 links in page content
    - Basic iframe extraction (common video player domains)

    Args:
        html_content: HTML content string
        base_url: Base URL for resolving relative URLs

    Returns:
        List of StreamCandidate objects with extracted URLs

    Raises:
        HTMLParseError: If HTML parsing fails
    """
    logger.debug(f"Extracting streams from HTML (base_url: {base_url})")

    try:
        soup = BeautifulSoup(html_content, "lxml")
    except Exception as e:
        logger.error(f"Failed to parse HTML: {e}")
        raise HTMLParseError(
            f"Failed to parse HTML content: {e}",
            "Unable to parse the webpage. The page may be malformed or unsupported.",
        ) from e

    streams: list[StreamCandidate] = []
    seen_urls: set[str] = set()

    # Extract from <video> tags
    for video_tag in soup.find_all("video"):
        # Check src attribute
        src_attr = video_tag.get("src")
        if src_attr and isinstance(src_attr, str):
            url = urljoin(base_url, src_attr)
            if url not in seen_urls:
                streams.append(StreamCandidate(url=url, source_type="video_tag"))
                seen_urls.add(url)
                logger.debug(f"Found stream in <video> src: {url}")

        # Check <source> children
        for source_tag in video_tag.find_all("source"):
            src_attr = source_tag.get("src")
            if src_attr and isinstance(src_attr, str):
                url = urljoin(base_url, src_attr)
                if url not in seen_urls:
                    streams.append(StreamCandidate(url=url, source_type="source_tag"))
                    seen_urls.add(url)
                    logger.debug(f"Found stream in <source> tag: {url}")

            # Check srcset attribute
            srcset_attr = source_tag.get("srcset")
            if srcset_attr and isinstance(srcset_attr, str):
                # Parse srcset (format: "url1 1x, url2 2x" or "url1 100w, url2 200w")
                for src_entry in srcset_attr.split(","):
                    url_part = src_entry.strip().split()[0]
                    url = urljoin(base_url, url_part)
                    if url not in seen_urls:
                        streams.append(StreamCandidate(url=url, source_type="source_tag"))
                        seen_urls.add(url)
                        logger.debug(f"Found stream in <source> srcset: {url}")

    # Extract from standalone <source> tags
    for source_tag in soup.find_all("source", recursive=False):
        src_attr = source_tag.get("src")
        if src_attr and isinstance(src_attr, str):
            url = urljoin(base_url, src_attr)
            if url not in seen_urls:
                streams.append(StreamCandidate(url=url, source_type="source_tag"))
                seen_urls.add(url)
                logger.debug(f"Found stream in standalone <source> tag: {url}")

    # Search for stream URLs in page content (including text nodes)
    stream_patterns = [
        (r"https?://[^\s\"'<>]+\.m3u8[^\s\"'<>]*", "m3u8_link"),
        (r"https?://[^\s\"'<>]+\.mp4[^\s\"'<>]*", "mp4_link"),
        (r"https?://[^\s\"'<>]+\.webm[^\s\"'<>]*", "webm_link"),
        (r"https?://[^\s\"'<>]+\.m3u[^\s\"'<>]*", "m3u_link"),
    ]

    # Search in page text content
    page_text = soup.get_text()
    for pattern, source_type in stream_patterns:
        for match in re.finditer(pattern, page_text, re.IGNORECASE):
            url = match.group(0)
            # Filter out URLs that are clearly not streams
            # (e.g., images, CSS, JS files)
            non_stream_exts = [".jpg", ".jpeg", ".png", ".gif", ".css", ".js", ".json"]
            if any(ext in url.lower() for ext in non_stream_exts):
                continue
            if url not in seen_urls:
                streams.append(StreamCandidate(url=url, source_type=source_type))
                seen_urls.add(url)
                logger.debug(f"Found {source_type} in page content: {url}")

    # Search for stream URLs in JavaScript code within <script> tags
    for script_tag in soup.find_all("script"):
        script_content = script_tag.string if script_tag.string else ""
        if not script_content:
            # Try to get content from script tag
            script_content = str(script_tag)

        for pattern, source_type in stream_patterns:
            for match in re.finditer(pattern, script_content, re.IGNORECASE):
                url = match.group(0)
                # Filter out non-stream URLs
                non_stream_exts = [".jpg", ".jpeg", ".png", ".gif", ".css", ".js", ".json"]
                if any(ext in url.lower() for ext in non_stream_exts):
                    continue
                if url not in seen_urls:
                    streams.append(StreamCandidate(url=url, source_type=f"script_{source_type}"))
                    seen_urls.add(url)
                    logger.debug(f"Found {source_type} in script tag: {url}")

    # Basic iframe extraction (common video player domains)
    common_player_domains = [
        "youtube.com",
        "youtu.be",
        "vimeo.com",
        "dailymotion.com",
        "twitch.tv",
    ]
    for iframe_tag in soup.find_all("iframe"):
        iframe_src = iframe_tag.get("src", "")
        if iframe_src and isinstance(iframe_src, str):
            parsed = urlparse(iframe_src)
            domain = parsed.netloc.lower()
            if any(player_domain in domain for player_domain in common_player_domains):
                # For now, we just log these - full player API integration is deferred
                logger.debug(f"Found iframe with video player domain: {domain}")
                # Note: Full iframe extraction would require player-specific APIs

    logger.info(f"Extracted {len(streams)} unique streams from HTML")
    return streams


def validate_url_accessibility(url: str, timeout: float = 15.0) -> URLValidationResult:
    """Validate that a URL is accessible.

    Performs HTTP HEAD request with timeout. Handles redirects up to 5 levels.
    Checks HTTP status codes (200-299 = accessible).

    Args:
        url: URL string to validate
        timeout: Timeout in seconds (default: 15.0)

    Returns:
        URLValidationResult with accessibility status and details

    Raises:
        URLValidationError: If validation fails (network error, etc.)
    """
    logger.debug(f"Validating URL accessibility: {url} (timeout: {timeout}s)")

    try:
        headers = _get_browser_headers(url)
        with httpx.Client(follow_redirects=True, timeout=timeout, headers=headers) as client:
            response = client.head(url, follow_redirects=True)

            # Track redirects
            redirect_count = len(response.history)
            if redirect_count > 5:
                logger.warning(f"URL exceeded 5 redirects: {redirect_count}")
                return URLValidationResult(
                    is_accessible=False,
                    status_code=response.status_code,
                    error_message=(
                        f"URL exceeded maximum redirect limit (5): " f"{redirect_count} redirects"
                    ),
                    content_type=response.headers.get("Content-Type"),
                )

            # Check status code
            is_accessible = 200 <= response.status_code < 300
            content_type = response.headers.get("Content-Type")

            if is_accessible:
                logger.debug(f"URL is accessible (status: {response.status_code})")
            else:
                logger.warning(f"URL is not accessible (status: {response.status_code})")

            return URLValidationResult(
                is_accessible=is_accessible,
                status_code=response.status_code,
                error_message=None if is_accessible else f"HTTP {response.status_code}",
                content_type=content_type,
            )

    except httpx.TimeoutException as e:
        logger.error(f"Timeout validating URL: {e}")
        raise URLValidationError(
            f"Timeout while validating URL: {url}",
            (
                f"The URL took too long to respond (timeout: {timeout}s). "
                "Please check your connection and try again."
            ),
        ) from e
    except httpx.ConnectError as e:
        logger.error(f"Connection error validating URL: {e}")
        raise URLValidationError(
            f"Connection error while validating URL: {url}",
            (
                "Unable to connect to the URL. "
                "Please check your internet connection and verify the URL is correct."
            ),
        ) from e
    except httpx.NetworkError as e:
        logger.error(f"Network error validating URL: {e}")
        raise URLValidationError(
            f"Network error while validating URL: {url}",
            "A network error occurred. Please check your internet connection and try again.",
        ) from e
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP status error validating URL: {e}")
        return URLValidationResult(
            is_accessible=False,
            status_code=e.response.status_code,
            error_message=f"HTTP {e.response.status_code}: {e}",
            content_type=e.response.headers.get("Content-Type"),
        )
    except httpx.HTTPError as e:
        logger.error(f"HTTP error validating URL: {e}")
        raise URLValidationError(
            f"HTTP error while validating URL: {url}",
            f"Unable to access the URL: {e}",
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error validating URL: {e}", exc_info=True)
        raise URLValidationError(
            f"Unexpected error while validating URL: {url}",
            "An unexpected error occurred. Please try again.",
        ) from e
