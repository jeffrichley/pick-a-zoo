"""CLI entry point for Pick-a-Zoo."""

from pick_a_zoo.tui.app import PickAZooApp


def main() -> None:
    """Entry point for pickazoo command."""
    app = PickAZooApp()
    app.run()


if __name__ == "__main__":
    main()
