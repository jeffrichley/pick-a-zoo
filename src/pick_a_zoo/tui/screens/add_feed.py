"""Add feed screen for Pick-a-Zoo TUI."""

import httpx
from loguru import logger
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Input, Label, ListItem, ListView, Static

from pick_a_zoo.core.feed_discovery import (
    FeedDiscoveryError,
    HTMLParseError,
    URLType,
    URLValidationError,
    detect_url_type,
    extract_streams_from_html,
    validate_url_accessibility,
)
from pick_a_zoo.core.feed_manager import load_feeds, resolve_duplicate_name, save_feeds
from pick_a_zoo.core.models import DEFAULT_WINDOW_SIZE, Feed


class AddFeedScreen(Screen):
    """Screen for adding new camera feeds."""

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
        ("q", "cancel", "Cancel"),
    ]

    def __init__(self) -> None:
        """Initialize AddFeedScreen."""
        super().__init__()
        self.feed_name: str | None = None
        self.feed_url: str | None = None
        self.current_state: str = "name_input"  # name_input, url_input, stream_selection, error
        self.stream_candidates: list = []
        self.error_message: str | None = None

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        with Container(id="add-feed-container"):
            with Vertical(id="add-feed-content"):
                yield Label("Add a New Cam Feed", id="title")
                yield Static("", id="status-message")
                yield Input(placeholder="Enter feed name...", id="name-input")
                yield Static("", id="url-prompt")
                yield Input(placeholder="Enter URL...", id="url-input", disabled=True)
                yield Static("", id="error-message")
                yield ListView(id="stream-list", disabled=True)

    def on_mount(self) -> None:
        """Called when screen is mounted. Initializes screen state and displays name prompt."""
        logger.info("AddFeedScreen mounted")
        self._update_display()
        # Focus on name input
        name_input = self.query_one("#name-input", Input)
        name_input.focus()

    def _update_display(self) -> None:
        """Update screen display based on current state."""
        status_widget = self.query_one("#status-message", Static)
        url_prompt = self.query_one("#url-prompt", Static)
        name_input = self.query_one("#name-input", Input)
        url_input = self.query_one("#url-input", Input)
        error_widget = self.query_one("#error-message", Static)
        stream_list = self.query_one("#stream-list", ListView)

        if self.current_state == "name_input":
            status_widget.update("Enter a name for this feed:")
            url_prompt.update("")
            name_input.disabled = False
            url_input.disabled = True
            error_widget.update("")
            stream_list.disabled = True
        elif self.current_state == "url_input":
            status_widget.update(f"Feed name: {self.feed_name}")
            url_prompt.update("Enter the URL for this feed:")
            name_input.disabled = True
            url_input.disabled = False
            error_widget.update("")
            stream_list.disabled = True
        elif self.current_state == "stream_selection":
            status_widget.update(f"Feed name: {self.feed_name}")
            url_prompt.update(f"Found {len(self.stream_candidates)} streams. Select one:")
            name_input.disabled = True
            url_input.disabled = True
            error_widget.update("")
            stream_list.disabled = False
            self._populate_stream_list()
        elif self.current_state == "error":
            status_widget.update(f"Feed name: {self.feed_name}")
            url_prompt.update("")
            name_input.disabled = True
            url_input.disabled = True
            error_widget.update(self.error_message or "An error occurred")
            stream_list.disabled = True

    def _populate_stream_list(self) -> None:
        """Populate stream list with candidates."""
        stream_list = self.query_one("#stream-list", ListView)
        stream_list.clear()
        for idx, candidate in enumerate(self.stream_candidates):
            stream_list.append(
                ListItem(
                    Label(f"{idx + 1}. {candidate.url} ({candidate.source_type})"),
                    id=f"stream-{idx}",
                )
            )

    @on(Input.Submitted, "#name-input")
    def on_name_submitted(self, event: Input.Submitted) -> None:
        """Handle name input submission."""
        name = event.value.strip()
        if not name:
            error_widget = self.query_one("#error-message", Static)
            error_widget.update("Feed name cannot be empty. Please enter a name.")
            return

        self.feed_name = name
        logger.info(f"Feed name entered: {self.feed_name}")
        self.current_state = "url_input"
        self._update_display()
        # Focus on URL input
        url_input = self.query_one("#url-input", Input)
        url_input.focus()

    @on(Input.Submitted, "#url-input")
    def on_url_submitted(self, event: Input.Submitted) -> None:
        """Handle URL input submission."""
        url = event.value.strip()
        if not url:
            error_widget = self.query_one("#error-message", Static)
            error_widget.update("URL cannot be empty. Please enter a URL.")
            return

        self.feed_url = url
        logger.info(f"URL entered: {self.feed_url}")

        # Update status to show validation in progress
        status_widget = self.query_one("#status-message", Static)
        status_widget.update("Validating URL...")

        try:
            # Detect URL type
            url_type = detect_url_type(url)

            if url_type == URLType.DIRECT_STREAM:
                # Validate accessibility
                validation_result = validate_url_accessibility(url)
                if validation_result.is_accessible:
                    # Create and save feed
                    self._save_direct_stream_feed(url)
                else:
                    # Show error and allow retry
                    self.current_state = "error"
                    error_msg = validation_result.error_message or "Unknown error"
                    self.error_message = (
                        f"URL is not accessible: {error_msg}. "
                        "Please check the URL and try again, or press 'q' to cancel."
                    )
                    self._update_display()
            else:
                # HTML page - fetch and extract streams
                self._handle_html_page(url)

        except URLValidationError as e:
            logger.error(f"URL validation error: {e}")
            self.current_state = "error"
            self.error_message = (
                f"Error validating URL: {e.user_message or str(e)}. "
                "Please check your connection and try again, or press 'q' to cancel."
            )
            self._update_display()
        except FeedDiscoveryError as e:
            logger.error(f"Feed discovery error: {e}")
            self.current_state = "error"
            self.error_message = (
                f"Error detecting URL type: {e.user_message or str(e)}. "
                "Please check the URL and try again, or press 'q' to cancel."
            )
            self._update_display()
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            self.current_state = "error"
            self.error_message = (
                f"An unexpected error occurred: {e}. " "Please try again or press 'q' to cancel."
            )
            self._update_display()

    def _handle_html_page(self, url: str) -> None:
        """Handle HTML page URL: fetch content and extract streams."""
        status_widget = self.query_one("#status-message", Static)
        status_widget.update("Fetching HTML page...")

        try:
            # Fetch HTML content with browser-like headers to avoid bot detection
            from pick_a_zoo.core.feed_discovery import _get_browser_headers

            headers = _get_browser_headers(url)
            with httpx.Client(timeout=30.0, follow_redirects=True, headers=headers) as client:
                response = client.get(url)
                response.raise_for_status()
                html_content = response.text

            logger.info(f"Fetched HTML content from {url} ({len(html_content)} bytes)")

            # Extract streams from HTML
            status_widget.update("Extracting streams from page...")
            self.stream_candidates = extract_streams_from_html(html_content, url)

            # Handle results
            if len(self.stream_candidates) == 0:
                # No streams found
                self.current_state = "error"
                self.error_message = (
                    "No playable streams found on this page. "
                    "Please try a different URL or provide a direct stream URL, "
                    "or press 'q' to cancel."
                )
                self._update_display()
            elif len(self.stream_candidates) == 1:
                # Single stream - auto-select and save
                logger.info(f"Single stream found, auto-selecting: {self.stream_candidates[0].url}")
                self._save_direct_stream_feed(self.stream_candidates[0].url)
            else:
                # Multiple streams - show selection list
                logger.info(f"Found {len(self.stream_candidates)} streams, showing selection list")
                self.current_state = "stream_selection"
                self._update_display()
                # Focus on stream list for keyboard navigation
                stream_list = self.query_one("#stream-list", ListView)
                stream_list.focus()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching HTML: {e}")
            # Try Playwright as fallback for 403 errors
            if e.response.status_code == 403:
                try:
                    from pick_a_zoo.core.feed_discovery import fetch_html_with_playwright

                    status_widget.update("Access denied. Trying with browser automation...")
                    logger.info("403 error detected, attempting Playwright fallback")
                    html_content = fetch_html_with_playwright(url, timeout=30.0)

                    # Extract streams from Playwright-fetched HTML
                    status_widget.update("Extracting streams from page...")
                    self.stream_candidates = extract_streams_from_html(html_content, url)

                    if len(self.stream_candidates) > 0:
                        # Found streams with Playwright!
                        if len(self.stream_candidates) == 1:
                            stream_url = self.stream_candidates[0].url
                            logger.info(
                                f"Single stream found with Playwright, "
                                f"auto-selecting: {stream_url}"
                            )
                            self._save_direct_stream_feed(stream_url)
                            return
                        else:
                            logger.info(
                                f"Found {len(self.stream_candidates)} streams "
                                "with Playwright, showing selection"
                            )
                            self.current_state = "stream_selection"
                            self._update_display()
                            stream_list = self.query_one("#stream-list", ListView)
                            stream_list.focus()
                            return
                    else:
                        # Playwright worked but no streams found
                        self.current_state = "error"
                        self.error_message = (
                            "Page loaded successfully but no playable streams were found. "
                            "The page may not contain embedded video streams, "
                            "or they may be loaded dynamically. "
                            "Please try a direct stream URL instead, "
                            "or press 'q' to cancel."
                        )
                        self._update_display()
                        return

                except Exception as playwright_error:
                    logger.warning(f"Playwright fallback failed: {playwright_error}")
                    # Fall through to error message below

            # Try to extract streams from error page HTML anyway
            # (some sites return HTML even on 403)
            if e.response.status_code == 403:
                try:
                    html_content = e.response.text
                    logger.info(
                        f"Attempting stream extraction from 403 response "
                        f"({len(html_content)} bytes)"
                    )
                    self.stream_candidates = extract_streams_from_html(html_content, url)
                    if len(self.stream_candidates) > 0:
                        # Found streams despite 403!
                        if len(self.stream_candidates) == 1:
                            stream_url = self.stream_candidates[0].url
                            logger.info(
                                f"Single stream found despite 403, " f"auto-selecting: {stream_url}"
                            )
                            self._save_direct_stream_feed(stream_url)
                            return
                        else:
                            logger.info(
                                f"Found {len(self.stream_candidates)} streams "
                                "despite 403, showing selection"
                            )
                            self.current_state = "stream_selection"
                            self._update_display()
                            stream_list = self.query_one("#stream-list", ListView)
                            stream_list.focus()
                            return
                except Exception as parse_error:
                    logger.warning(f"Failed to parse 403 response: {parse_error}")

            # No streams found or parsing failed
            self.current_state = "error"
            if e.response.status_code == 403:
                self.error_message = (
                    "Access denied (403 Forbidden). "
                    "The site may be blocking automated requests. "
                    "Browser automation (Playwright) was attempted but failed. "
                    "Try accessing the page in a browser first, "
                    "or provide a direct stream URL instead. "
                    "Press 'q' to cancel."
                )
            else:
                self.error_message = (
                    f"Failed to fetch page: HTTP {e.response.status_code}. "
                    "Please check the URL and try again, or press 'q' to cancel."
                )
            self._update_display()
        except httpx.TimeoutException as e:
            logger.error(f"Timeout fetching HTML: {e}")
            self.current_state = "error"
            self.error_message = (
                "Request timed out while fetching the page. "
                "Please check your connection and try again, or press 'q' to cancel."
            )
            self._update_display()
        except httpx.RequestError as e:
            logger.error(f"Network error fetching HTML: {e}")
            self.current_state = "error"
            self.error_message = (
                f"Network error: {e}. "
                "Please check your connection and try again, or press 'q' to cancel."
            )
            self._update_display()
        except HTMLParseError as e:
            logger.error(f"HTML parse error: {e}")
            self.current_state = "error"
            self.error_message = (
                f"Failed to parse HTML page: {e.user_message or str(e)}. "
                "Please try a different URL or provide a direct stream URL, or press 'q' to cancel."
            )
            self._update_display()
        except Exception as e:
            logger.error(f"Unexpected error handling HTML page: {e}", exc_info=True)
            self.current_state = "error"
            self.error_message = (
                f"An unexpected error occurred: {e}. " "Please try again or press 'q' to cancel."
            )
            self._update_display()

    def _save_direct_stream_feed(self, url: str) -> None:
        """Save a direct stream feed."""
        try:
            # Load existing feeds
            existing_feeds = load_feeds()

            # Resolve duplicate name
            resolved_name = resolve_duplicate_name(self.feed_name or "Unnamed Feed", existing_feeds)

            # Create feed with default window size
            feed = Feed(name=resolved_name, url=url, window_size=DEFAULT_WINDOW_SIZE)

            # Add to list and save
            existing_feeds.append(feed)
            save_feeds(existing_feeds)

            logger.info(f"Feed saved: {resolved_name} -> {url}")

            # Show success message and return to main menu
            status_widget = self.query_one("#status-message", Static)
            status_widget.update(f"Feed '{resolved_name}' saved successfully!")
            self.app.pop_screen()

        except Exception as e:
            logger.error(f"Error saving feed: {e}", exc_info=True)
            self.current_state = "error"
            self.error_message = (
                f"Error saving feed: {e}. " "Please try again or press 'q' to cancel."
            )
            self._update_display()

    @on(ListView.Selected, "#stream-list")
    def on_stream_selected(self, event: ListView.Selected) -> None:
        """Handle stream selection from list."""
        selected_item = event.item
        if selected_item and selected_item.id:
            # Extract stream index from ID (format: "stream-{idx}")
            stream_idx = int(selected_item.id.split("-")[1])
            if 0 <= stream_idx < len(self.stream_candidates):
                selected_stream = self.stream_candidates[stream_idx]
                # Save feed with selected stream URL
                self._save_direct_stream_feed(selected_stream.url)

    def action_cancel(self) -> None:
        """Handle cancellation - return to main menu."""
        logger.info("AddFeedScreen cancelled")
        self.app.pop_screen()
