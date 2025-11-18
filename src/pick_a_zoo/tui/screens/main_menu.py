"""Main menu screen for Pick-a-Zoo TUI."""

from loguru import logger
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Label, ListItem, ListView, Static

from pick_a_zoo.core.feed_manager import load_feeds
from pick_a_zoo.tui.screens.add_feed import AddFeedScreen


class MainMenuScreen(Screen):
    """Main menu screen displaying navigation options."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
        ("1", "select_option(0)", "Option 1"),
        ("2", "select_option(1)", "Option 2"),
        ("3", "select_option(2)", "Option 3"),
        ("4", "select_option(3)", "Option 4"),
        ("v", "select_view", "View"),
        ("a", "select_add", "Add"),
        ("w", "select_watch", "Watch"),
        ("up", "navigate_up", "Up"),
        ("down", "navigate_down", "Down"),
    ]

    MENU_OPTIONS = [
        ("View Saved Cams", "view", "v"),
        ("Add a New Cam", "add", "a"),
        ("Watch a Cam", "watch", "w"),
        ("Quit", "quit", "q"),
    ]

    MIN_TERMINAL_WIDTH = 80
    MIN_TERMINAL_HEIGHT = 24

    def compose(self) -> ComposeResult:
        """Compose the screen layout."""
        with Container(id="main-container"):
            with Vertical(id="menu-container"):
                yield Label("Pick-a-Zoo", id="title")
                yield Static("", id="status-message")
                yield ListView(id="menu-list")
                yield Static("", id="terminal-warning")

    def on_mount(self) -> None:
        """Called when screen is mounted. Loads feeds and updates display."""
        logger.info("Main menu screen mounted")
        self._load_feeds_and_update_display()
        self._setup_menu()
        self._check_terminal_size()

    def _load_feeds_and_update_display(self) -> None:
        """Load feeds and update status message."""
        try:
            feeds = load_feeds()
            status_widget = self.query_one("#status-message", Static)

            if not feeds:
                status_widget.update("No cams saved yet")
                logger.info("No feeds found, displaying empty state")
            else:
                feed_count = len(feeds)
                status_widget.update(f"{feed_count} cam{'s' if feed_count != 1 else ''} saved")
                logger.info(f"Loaded {feed_count} feeds")
        except Exception as e:
            logger.error(f"Failed to load feeds: {e}", exc_info=True)
            status_widget = self.query_one("#status-message", Static)
            status_widget.update("No cams saved yet")
            # Continue normally even if feed loading fails

    def _setup_menu(self) -> None:
        """Set up the menu list with options."""
        menu_list = self.query_one("#menu-list", ListView)
        for option_text, option_id, _ in self.MENU_OPTIONS:
            menu_list.append(ListItem(Label(option_text), id=option_id))

    def _check_terminal_size(self) -> None:
        """Check terminal size and display warning if too small."""
        terminal_warning = self.query_one("#terminal-warning", Static)
        size = self.app.size

        if size.width < self.MIN_TERMINAL_WIDTH or size.height < self.MIN_TERMINAL_HEIGHT:
            warning_msg = (
                f"Warning: Terminal size ({size.width}x{size.height}) is below "
                f"recommended minimum ({self.MIN_TERMINAL_WIDTH}x{self.MIN_TERMINAL_HEIGHT})"
            )
            terminal_warning.update(warning_msg)
            logger.warning(f"Terminal size below minimum: {size.width}x{size.height}")
        else:
            terminal_warning.update("")

    @on(ListView.Selected)
    def on_menu_selected(self, event: ListView.Selected) -> None:
        """Handle menu option selection."""
        selected_item = event.item
        option_id = selected_item.id if selected_item else None

        if option_id:
            logger.info(f"Menu option selected: {option_id}")
            self.action_select_option_by_id(option_id)

    def action_select_option_by_id(self, option: str) -> None:
        """Handle menu option selection routing.

        Args:
            option: Selected option identifier ("view", "add", "watch", "quit")
        """
        if option == "quit":
            self.action_quit()
        elif option == "view":
            logger.info("View Saved Cams selected (not yet implemented)")
            # Future: push ViewSavedCamsScreen()
        elif option == "add":
            logger.info("Add a New Cam selected")
            self.app.push_screen(AddFeedScreen())
        elif option == "watch":
            logger.info("Watch a Cam selected (not yet implemented)")
            # Future: push WatchCamScreen()
        else:
            logger.warning(f"Unknown option selected: {option}")

    def action_quit(self) -> None:
        """Quit the application."""
        logger.info("Quit action triggered")
        self.app.exit()

    def action_select_option(self, index: int) -> None:
        """Select a menu option by index (bound to number keys).

        Args:
            index: Zero-based index of the menu option
        """
        if 0 <= index < len(self.MENU_OPTIONS):
            menu_list = self.query_one("#menu-list", ListView)
            menu_list.index = index
            option_id = self.MENU_OPTIONS[index][1]
            self.action_select_option_by_id(option_id)

    def action_select_view(self) -> None:
        """Select View Saved Cams option."""
        self.action_select_option_by_id("view")

    def action_select_add(self) -> None:
        """Select Add a New Cam option."""
        self.action_select_option_by_id("add")

    def action_select_watch(self) -> None:
        """Select Watch a Cam option."""
        self.action_select_option_by_id("watch")

    def action_navigate_up(self) -> None:
        """Navigate menu up (WASD: W key)."""
        menu_list = self.query_one("#menu-list", ListView)
        current_index = menu_list.index
        if current_index is not None and current_index > 0:
            menu_list.index = current_index - 1

    def action_navigate_down(self) -> None:
        """Navigate menu down (WASD: S key)."""
        menu_list = self.query_one("#menu-list", ListView)
        current_index = menu_list.index
        if current_index is not None and current_index < len(self.MENU_OPTIONS) - 1:
            menu_list.index = current_index + 1
