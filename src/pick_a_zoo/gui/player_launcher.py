"""Standalone launcher for PyQt video player windows.

This module runs as a separate process to avoid conflicts with the Textual TUI.
It creates a QApplication in the main thread and displays a video window.
"""

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    pass

# Suppress Qt warnings from polluting stdout/stderr
# These will be redirected when launched from subprocess
os.environ.setdefault("QT_LOGGING_RULES", "*.debug=false;qt.*.debug=false")

# Set up logging to a file so we can diagnose issues
# Log file goes to .pickazoo/player_launcher.log
_log_dir = Path.cwd() / ".pickazoo"
_log_dir.mkdir(parents=True, exist_ok=True)
_log_file = _log_dir / "player_launcher.log"

# Configure loguru to write to file
logger.add(
    _log_file,
    rotation="10 MB",
    retention="3 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)


def main() -> None:
    """Main entry point for player launcher process.

    Expected command-line arguments:
        sys.argv[1]: feed_name (string)
        sys.argv[2]: stream_url (string)
        sys.argv[3]: width (int, optional, default: 1280)
        sys.argv[4]: height (int, optional, default: 720)

    Behavior:
        - Creates QApplication in main thread (required by Qt)
        - Creates and shows VideoWindow
        - Runs Qt event loop until window closed
        - Exits cleanly when window closes
    """
    if len(sys.argv) < 3:
        usage_msg = (
            "Usage: python -m pick_a_zoo.gui.player_launcher "
            "<feed_name> <stream_url> [width] [height]"
        )
        print(usage_msg, file=sys.stderr)
        sys.exit(1)

    feed_name = sys.argv[1]
    stream_url = sys.argv[2]
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 1280
    height = int(sys.argv[4]) if len(sys.argv) > 4 else 720

    try:
        from PyQt6.QtWidgets import QApplication

        from pick_a_zoo.gui.video_window import VideoWindow

        # Create QApplication in main thread (required by Qt)
        app = QApplication(sys.argv)

        # Create and show video window
        logger.info(
            f"Creating video window for feed: {feed_name}, "
            f"URL: {stream_url}, size: {width}x{height}"
        )
        window = VideoWindow(feed_name, stream_url, width, height)
        window.show()
        logger.info(f"Video window shown for feed: {feed_name}")

        # Run Qt event loop
        logger.info("Starting Qt event loop")
        exit_code = app.exec()
        logger.info(f"Qt event loop exited with code: {exit_code}")
        sys.exit(exit_code)

    except ImportError as e:
        logger.error(f"PyQt6 not available: {e}")
        print(f"Error: PyQt6 is required for video windows: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to launch video player: {e}", exc_info=True)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
