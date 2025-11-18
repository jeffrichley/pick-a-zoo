"""View Saved Cams screen for displaying and navigating saved camera feeds."""

from urllib.parse import urlparse

from loguru import logger
from textual import on
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import ListItem, ListView, Static

from pick_a_zoo.core.feed_manager import load_feeds
from pick_a_zoo.core.models import Feed


def _is_valid_url(url: str) -> bool:
    """Check if a URL string is valid.

    Args:
        url: URL string to validate

    Returns:
        True if URL is non-empty and has valid format, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    if not url:
        return False
    try:
        result = urlparse(url)
        # Check that URL has at least a scheme or netloc
        return bool(result.scheme and result.netloc) or bool(result.netloc)
    except Exception:
        return False


class ViewSavedCamsScreen(Screen):
    """Screen for viewing and navigating saved camera feeds."""

    BINDINGS = [
        ("escape", "return_to_menu", "Back"),
        ("q", "return_to_menu", "Back"),
        ("w", "navigate_up", "Up"),
        ("s", "navigate_down", "Down"),
        ("a", "navigate_left", "Left"),
        ("d", "navigate_right", "Right"),
    ]

    def __init__(self, *args, **kwargs):
        """Initialize the screen."""
        super().__init__(*args, **kwargs)
        self._feeds: list[Feed] = []  # Store feeds for selection handling

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        yield ListView(id="feeds-list")
        yield Static("", id="empty-message")
        yield Static("", id="error-message")

    def on_mount(self) -> None:
        """Called when screen is mounted. Loads feeds and updates display."""
        import time

        start_time = time.time()
        logger.info("ViewSavedCamsScreen mounted, loading feeds")
        try:
            feeds = load_feeds()
            logger.debug(f"load_feeds() returned {len(feeds)} feeds")
            valid_feeds = self._filter_valid_feeds(feeds)
            logger.debug(f"After filtering: {len(valid_feeds)} valid feeds")
            if not valid_feeds:
                self._show_empty_state()
                elapsed = time.time() - start_time
                logger.info(f"Feed loading completed in {elapsed:.3f}s (empty state)")
                return

            sorted_feeds = self._sort_feeds(valid_feeds)
            self._feeds = sorted_feeds  # Store for selection handling
            logger.debug(f"About to populate list with {len(sorted_feeds)} feeds")
            self._populate_list(sorted_feeds)
            elapsed = time.time() - start_time
            logger.info(f"Loaded and displayed {len(sorted_feeds)} feeds in {elapsed:.3f}s")
        except PermissionError as e:
            logger.error(f"Permission denied loading feeds: {e}", exc_info=True)
            self._show_error("Cannot read configuration file. Check permissions.")
        except OSError as e:
            logger.error(f"OS error loading feeds: {e}", exc_info=True)
            self._show_error(
                "Failed to read configuration file. File may be locked or inaccessible."
            )
        except Exception as e:
            logger.error(f"Unexpected error loading feeds: {e}", exc_info=True)
            # Show more detailed error message to help debug
            error_detail = str(e)
            if len(error_detail) > 100:
                error_detail = error_detail[:100] + "..."
            self._show_error(f"Failed to load feeds: {error_detail}")

    def _filter_valid_feeds(self, feeds: list[Feed]) -> list[Feed]:
        """Filter out feeds with invalid or missing URLs.

        Args:
            feeds: List of Feed objects to filter

        Returns:
            List of Feed objects with valid URLs
        """
        valid_feeds = []
        for feed in feeds:
            if feed.url and _is_valid_url(str(feed.url)):
                valid_feeds.append(feed)
            else:
                logger.warning(f"Skipping feed with invalid URL: {feed.name}")
        return valid_feeds

    def _sort_feeds(self, feeds: list[Feed]) -> list[Feed]:
        """Sort feeds alphabetically by name (case-insensitive).

        Args:
            feeds: List of Feed objects to sort

        Returns:
            Sorted list of Feed objects
        """
        return sorted(feeds, key=lambda f: f.name.lower())

    def _resolve_duplicate_names(self, feeds: list[Feed]) -> list[tuple[Feed, str]]:
        """Resolve duplicate feed names by adding number suffixes.

        Args:
            feeds: List of Feed objects

        Returns:
            List of tuples (Feed, display_name) with resolved names
        """
        name_counts: dict[str, int] = {}
        result = []

        for feed in feeds:
            base_name = feed.name
            if base_name in name_counts:
                name_counts[base_name] += 1
                display_name = f"{base_name} ({name_counts[base_name]})"
            else:
                name_counts[base_name] = 1
                display_name = base_name
            result.append((feed, display_name))

        return result

    def _truncate_name(self, name: str, max_width: int) -> str:
        """Truncate long names with ellipsis.

        Args:
            name: Name to truncate
            max_width: Maximum width for the name

        Returns:
            Truncated name with ellipsis if needed
        """
        if len(name) <= max_width:
            return name
        return name[: max_width - 3] + "..."

    def _populate_list(self, feeds: list[Feed]) -> None:
        """Populate the ListView with feed items.

        Args:
            feeds: List of Feed objects to display
        """
        try:
            list_view = self.query_one("#feeds-list", ListView)
        except Exception as e:
            logger.error(f"Failed to query feeds-list: {e}", exc_info=True)
            raise

        list_view.clear()

        # Resolve duplicate names
        feeds_with_names = self._resolve_duplicate_names(feeds)

        # Get terminal width for truncation
        # Use app.size as screen size might not be available yet
        try:
            if hasattr(self, "app") and self.app and hasattr(self.app, "size") and self.app.size:
                terminal_width = self.app.size.width
            else:
                terminal_width = 80
        except (AttributeError, TypeError) as e:
            logger.debug(f"Could not get terminal width: {e}, using default 80")
            terminal_width = 80
        # Account for emoji (2 chars) and padding (2 chars)
        max_name_width = max(20, terminal_width - 4)

        for idx, (feed, display_name) in enumerate(feeds_with_names):
            # Truncate name if needed
            truncated_name = self._truncate_name(display_name, max_name_width)
            # Add emoji icon
            display_text = f"📹 {truncated_name}"

            # Create ListItem with index as id for selection handling
            # Use "feed-" prefix to ensure valid CSS identifier (can't start with number)
            list_item = ListItem(Static(display_text), id=f"feed-{idx}")
            list_view.append(list_item)

        # Show list, hide empty/error messages
        list_view.visible = True
        empty_msg = self.query_one("#empty-message", Static)
        empty_msg.visible = False
        error_msg = self.query_one("#error-message", Static)
        error_msg.visible = False

    def _show_empty_state(self) -> None:
        """Display empty state message when no feeds exist."""
        empty_msg = self.query_one("#empty-message", Static)
        empty_msg.update("No feeds saved.\n\nUse 'Add a New Cam' to add feeds.")
        empty_msg.visible = True

        list_view = self.query_one("#feeds-list", ListView)
        list_view.visible = False
        error_msg = self.query_one("#error-message", Static)
        error_msg.visible = False

        logger.info("Displaying empty state")

    def _show_error(self, error_text: str) -> None:
        """Display error message.

        Args:
            error_text: Error message to display
        """
        try:
            error_msg = self.query_one("#error-message", Static)
            error_msg.update(f"Error: {error_text}\n\nPress Escape or Q to return to menu.")
            error_msg.visible = True

            try:
                list_view = self.query_one("#feeds-list", ListView)
                list_view.visible = False
            except Exception:
                pass  # ListView might not exist

            try:
                empty_msg = self.query_one("#empty-message", Static)
                empty_msg.visible = False
            except Exception:
                pass  # Empty message might not exist

            logger.error(f"Displaying error: {error_text}")
        except Exception as e:
            # If we can't display the error, at least log it
            logger.error(
                f"Failed to display error message: {e}. Original error: {error_text}",
                exc_info=True,
            )

    def action_return_to_menu(self) -> None:
        """Return to main menu."""
        logger.info("Returning to main menu")
        self.app.pop_screen()

    def action_navigate_up(self) -> None:
        """Navigate list up (WASD: W key)."""
        list_view = self.query_one("#feeds-list", ListView)
        current_index = list_view.index
        if current_index is not None and current_index > 0:
            list_view.index = current_index - 1

    def action_navigate_down(self) -> None:
        """Navigate list down (WASD: S key)."""
        list_view = self.query_one("#feeds-list", ListView)
        current_index = list_view.index
        if current_index is not None:
            max_index = len(list_view.children) - 1
            if current_index < max_index:
                list_view.index = current_index + 1

    def action_navigate_left(self) -> None:
        """Navigate list left (WASD: A key)."""
        # For vertical list, left/right don't do anything, but we implement for consistency
        pass

    def action_navigate_right(self) -> None:
        """Navigate list right (WASD: D key)."""
        # For vertical list, left/right don't do anything, but we implement for consistency
        pass

    @on(ListView.Selected)
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle feed selection from list.

        Args:
            event: ListView selection event
        """
        selected_item = event.item
        if selected_item and selected_item.id:
            try:
                # Extract index from "feed-{idx}" format
                if selected_item.id.startswith("feed-"):
                    feed_index = int(selected_item.id[5:])  # Remove "feed-" prefix
                else:
                    # Fallback for old format (shouldn't happen, but be safe)
                    feed_index = int(selected_item.id)

                if 0 <= feed_index < len(self._feeds):
                    feed = self._feeds[feed_index]
                    logger.info(f"Feed selected: {feed.name} ({feed.url})")
                    # Placeholder for Story 4: transition to watch action
                    # TODO: Push WatchCamScreen(feed) when Story 4 is implemented
                    logger.debug("Feed selection - watch action not yet implemented (Story 4)")
            except (ValueError, IndexError) as e:
                logger.warning(f"Invalid feed index: {selected_item.id}: {e}")

