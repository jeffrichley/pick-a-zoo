# Feed Discovery Contract

**Module**: `pick_a_zoo.core.feed_discovery`  
**Type**: Internal Library API  
**Constitution**: Library-First Architecture (Principle II)

## Overview

The Feed Discovery module is a standalone library responsible for detecting URL types (direct stream vs HTML page), extracting stream URLs from HTML pages, and validating URL accessibility. It follows the library-first architecture principle and is independently testable.

## Interface

### `detect_url_type(url: str) -> URLType`

Detects whether a URL is a direct stream or an HTML webpage.

**Parameters**:
- `url` (str): URL string to analyze

**Returns**: `URLType` enum value (`DIRECT_STREAM` or `HTML_PAGE`)

**Behavior**:
- First checks URL pattern (extension, protocol) for known stream formats
- If pattern matches stream format → returns `DIRECT_STREAM`
- If pattern doesn't match → performs HTTP HEAD request to check Content-Type
- If Content-Type is `text/html` → returns `HTML_PAGE`
- If Content-Type is `video/*` or `application/vnd.apple.mpegurl` → returns `DIRECT_STREAM`
- Follows redirects (up to 5 redirects)

**Raises**:
- `FeedDiscoveryError`: If detection fails (network error, invalid URL format, etc.)

**Side Effects**:
- May perform HTTP HEAD request (network I/O)
- Logs detection process via structured logging

**Example**:
```python
from pick_a_zoo.core.feed_discovery import detect_url_type, URLType

url_type = detect_url_type("https://example.org/stream.m3u8")
# Returns: URLType.DIRECT_STREAM

url_type = detect_url_type("https://example.org/cam-page.html")
# Returns: URLType.HTML_PAGE
```

### `extract_streams_from_html(html_content: str, base_url: str) -> list[StreamCandidate]`

Extracts stream URLs from HTML content.

**Parameters**:
- `html_content` (str): HTML content to parse
- `base_url` (str): Base URL for resolving relative URLs

**Returns**: List of `StreamCandidate` objects (may be empty if no streams found)

**Behavior**:
- Parses HTML with BeautifulSoup4 (lxml backend)
- Extracts from `<video>` tags: looks for `src` attribute and `<source>` children
- Extracts from `<source>` tags: looks for `src` and `srcset` attributes
- Searches page content for m3u8 URLs (regex pattern)
- Extracts from embedded iframes: checks common video player domains (basic support)
- Filters out non-stream URLs (images, static files)
- Resolves relative URLs to absolute URLs using base_url
- Returns deduplicated list of stream candidates

**Raises**:
- `HTMLParseError`: If HTML parsing fails (malformed HTML, encoding issues, etc.)

**Side Effects**:
- None (pure parsing operation)

**Example**:
```python
from pick_a_zoo.core.feed_discovery import extract_streams_from_html

html = """
<html>
  <video src="https://example.org/stream.m3u8"></video>
  <source src="https://example.org/backup.mp4">
</html>
"""
streams = extract_streams_from_html(html, "https://example.org/")
# Returns: [
#   StreamCandidate(url="https://example.org/stream.m3u8", source_type="video_tag"),
#   StreamCandidate(url="https://example.org/backup.mp4", source_type="source_tag")
# ]
```

### `validate_url_accessibility(url: str, timeout: float = 15.0) -> URLValidationResult`

Validates that a URL is accessible.

**Parameters**:
- `url` (str): URL to validate
- `timeout` (float): Timeout in seconds (default: 15.0)

**Returns**: `URLValidationResult` object with accessibility status

**Behavior**:
- Performs HTTP HEAD request with timeout
- Follows redirects (up to 5 redirects)
- Checks HTTP status code (200-299 = accessible, others = error)
- Captures Content-Type header if available
- Handles network errors (timeout, connection refused, DNS failure)
- Does NOT validate authentication (deferred to playback time)

**Raises**:
- `URLValidationError`: If validation fails critically (not for normal failures - use result object)

**Side Effects**:
- Performs HTTP HEAD request (network I/O)
- Logs validation process via structured logging

**Example**:
```python
from pick_a_zoo.core.feed_discovery import validate_url_accessibility

result = validate_url_accessibility("https://example.org/stream.m3u8")
if result.is_accessible:
    print(f"URL is accessible: {result.status_code}")
else:
    print(f"URL not accessible: {result.error_message}")
```

## Data Types

### `URLType` (Enum)

Enumeration for URL type classification.

**Values**:
- `DIRECT_STREAM`: URL is a direct stream (m3u8, mp4, webm, rtsp, etc.)
- `HTML_PAGE`: URL is an HTML webpage containing embedded streams

### `StreamCandidate`

Represents a candidate stream URL extracted from HTML.

**Fields**:
- `url: str` - Extracted stream URL (absolute)
- `source_type: str` - How it was found ("video_tag", "source_tag", "m3u8_link", "iframe")

### `URLValidationResult`

Represents the result of validating a URL's accessibility.

**Fields**:
- `is_accessible: bool` - Whether URL is accessible
- `status_code: int | None` - HTTP status code if available
- `error_message: str | None` - Error message if validation failed
- `content_type: str | None` - Content-Type header if available

## Exception Types

### `FeedDiscoveryError`

Base exception for feed discovery errors.

**Attributes**:
- `message: str` - User-friendly error message
- `original_error: Exception | None` - Original exception if wrapped

### `HTMLParseError`

Exception raised when HTML parsing fails.

**Inherits from**: `FeedDiscoveryError`

### `URLValidationError`

Exception raised when URL validation fails critically.

**Inherits from**: `FeedDiscoveryError`

## Error Handling

All functions use structured logging (loguru) for errors and warnings. Functions raise custom exceptions (`FeedDiscoveryError`, `HTMLParseError`, `URLValidationError`) with user-friendly messages. Network errors are caught and converted to appropriate exception types.

## Testing Contract

Unit tests must cover:
- Direct stream URL detection (various formats: m3u8, mp4, webm, rtsp)
- HTML page URL detection (via Content-Type header)
- Stream extraction from HTML (video tags, source tags, m3u8 links)
- URL validation (accessible URLs, inaccessible URLs, timeouts)
- Error handling (network errors, parsing errors, invalid URLs)
- Redirect handling (up to 5 redirects)
- Relative URL resolution

## Dependencies

- `httpx`: HTTP client for URL validation and HTML fetching
- `beautifulsoup4`: HTML parsing for stream extraction
- `lxml`: HTML parser backend (faster, more robust)

