"""TUI Application root for Pick-a-Zoo."""

from textual.app import App

from pick_a_zoo.tui.screens.main_menu import MainMenuScreen


class PickAZooApp(App):
    """Main Textual application for Pick-a-Zoo."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        """Called when app starts. Loads feeds and displays main menu."""
        self.push_screen(MainMenuScreen())

    async def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
