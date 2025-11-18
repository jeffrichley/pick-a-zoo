"""Video window GUI component for displaying video streams.

This module provides PyQt6-based video windows that use the video_player library
for playback logic. Video windows run in separate processes launched from the TUI
to avoid conflicts with Textual's terminal control.
"""

from typing import TYPE_CHECKING

from loguru import logger

from pick_a_zoo.core.video_player import (
    MAX_WINDOW_HEIGHT,
    MAX_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    StreamLoadError,
    VideoPlayer,
    VideoPlayerError,
)

if TYPE_CHECKING:
    from PyQt6.QtCore import QTimer
    from PyQt6.QtGui import QCloseEvent, QResizeEvent


class VideoWindow:
    """PyQt6 QMainWindow subclass for video display."""

    def __init__(
        self, feed_name: str, stream_url: str, width: int = 1280, height: int = 720
    ) -> None:
        """Initialize video window with feed information and dimensions.

        Args:
            feed_name: Name of the feed being displayed (for window title)
            stream_url: URL of the video stream to play
            width: Initial window width in pixels (default: 1280)
            height: Initial window height in pixels (default: 720)

        Behavior:
            - Creates QMainWindow with video display area
            - Sets window title to feed name
            - Sets minimum size to 320x240, maximum to 7680x4320
            - Initializes video player library
            - Sets up resize event handlers

        Side Effects:
            - Window created but not shown (call show() to display)
            - Logs window creation via structured logging
        """
        try:
            from PyQt6.QtCore import Qt
            from PyQt6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

            # Create QMainWindow instance (using composition)
            self._window = QMainWindow()
            self.feed_name = feed_name
            self.stream_url = stream_url
            self._current_width = width
            self._current_height = height

            # Set window properties
            self._window.setWindowTitle(feed_name)
            self._window.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
            self._window.setMaximumSize(MAX_WINDOW_WIDTH, MAX_WINDOW_HEIGHT)
            self._window.resize(width, height)

            # Create central widget for video display
            central_widget = QWidget()
            self._window.setCentralWidget(central_widget)

            layout = QVBoxLayout(central_widget)
            layout.setContentsMargins(0, 0, 0, 0)

            # Video display label
            self.video_label = QLabel()
            self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.video_label.setStyleSheet("background-color: black;")
            layout.addWidget(self.video_label)

            # Error label (initially hidden)
            self.error_label = QLabel()
            self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_style = (
                "background-color: rgba(0, 0, 0, 200); "
                "color: white; font-size: 14px; padding: 20px;"
            )
            self.error_label.setStyleSheet(error_style)
            self.error_label.setWordWrap(True)
            self.error_label.hide()
            layout.addWidget(self.error_label)

            # Initialize video player
            self._player: VideoPlayer | None = None

            # Resize debouncing
            self._resize_timer: QTimer | None = None

            # Override window event handlers to forward to our methods
            original_close = self._window.closeEvent

            def wrapped_close(event: "QCloseEvent | None") -> None:
                self.closeEvent(event)
                # Call original handler if event wasn't accepted
                if event and not event.isAccepted():
                    original_close(event)

            original_resize = self._window.resizeEvent

            def wrapped_resize(event: "QResizeEvent | None") -> None:
                self.resizeEvent(event)
                # Call original handler
                original_resize(event)

            self._window.closeEvent = wrapped_close  # type: ignore[assignment]
            self._window.resizeEvent = wrapped_resize  # type: ignore[assignment]

            logger.info(f"VideoWindow initialized for feed: {feed_name}")
        except ImportError as e:
            logger.error(f"PyQt6 not available: {e}")
            raise RuntimeError("PyQt6 is required for video windows") from e

    def show(self) -> None:
        """Display the video window and start playback.

        Returns:
            None

        Behavior:
            - Shows the window
            - Starts loading stream automatically (FR-002)
            - Begins playback when stream loaded
            - Displays error if stream fails to load

        Side Effects:
            - Window becomes visible
            - Stream loading initiated
            - Logs show event via structured logging
        """
        self._window.show()
        logger.info(f"Video window shown for feed: {self.feed_name}")

        # Show loading status
        self._show_status("Loading stream...")

        # Start loading and playing stream
        try:
            logger.info(f"Creating VideoPlayer for URL: {self.stream_url}")
            self._player = VideoPlayer(self.stream_url)

            logger.info("Calling player.load()...")
            self._player.load()
            logger.info("Stream loaded successfully")

            logger.info("Calling player.play()...")
            self._player.play()
            logger.info("Playback started")

            # Start frame update timer
            self._start_frame_timer()
            logger.info("Frame update timer started")
        except (StreamLoadError, VideoPlayerError) as e:
            logger.error(f"Failed to load stream: {e}", exc_info=True)
            self.display_error(f"Failed to load stream: {e.message}")
        except Exception as e:
            logger.error(f"Unexpected error loading stream: {e}", exc_info=True)
            self.display_error(f"Unexpected error: {str(e)}")

    def _start_frame_timer(self) -> None:
        """Start timer to update video frames."""
        try:
            from PyQt6.QtCore import QTimer

            if self._player is None:
                return

            timer = QTimer(self._window)
            timer.timeout.connect(self._update_frame)
            timer.start(33)  # ~30 FPS (33ms per frame)
            self._frame_timer = timer
        except ImportError:
            pass

    def _update_frame(self) -> None:
        """Update video frame display."""
        if self._player is None:
            logger.debug("_update_frame: player is None")
            return

        if not self._player.is_playing():
            logger.debug("_update_frame: player is not playing")
            return

        try:
            frame = self._player.get_frame()
            if frame is None:
                # First time we get None, log it for diagnostics
                if not hasattr(self, "_frame_none_count"):
                    self._frame_none_count = 0
                self._frame_none_count += 1
                if self._frame_none_count == 1:
                    logger.debug("get_frame() returned None (waiting for frames...)")
                elif self._frame_none_count % 100 == 0:  # Log every 100th None
                    count = self._frame_none_count
                    logger.warning(f"Still getting None frames after {count} attempts")
                return

            # Reset None counter when we get a frame
            if hasattr(self, "_frame_none_count"):
                if self._frame_none_count > 0:
                    logger.info(f"Got first frame after {self._frame_none_count} attempts")
                self._frame_none_count = 0

            # Check for errors
            error = self._player.get_error()
            if error:
                logger.error(f"Player error detected: {error.message}")
                self.display_error(f"Playback error: {error.message}")
                return

            # Convert frame to QPixmap and display
            # ffpyplayer returns numpy array, convert to QImage
            import numpy as np
            from PyQt6.QtCore import Qt
            from PyQt6.QtGui import QImage, QPixmap

            # Handle different image formats
            img = frame.pixels

            # Handle ffpyplayer.pic.Image objects
            img_type_name = type(img).__name__
            if img_type_name == "Image" or "ffpyplayer" in str(type(img)):
                logger.debug(f"Frame pixels is ffpyplayer Image object: {type(img)}")

                # ffpyplayer.pic.Image API:
                # - get_pixel_array() returns numpy array directly (preferred)
                # - to_bytearray() returns (byte_data, format) tuple
                # - get_size() returns (width, height) tuple

                # Try get_pixel_array first (returns numpy array directly)
                if hasattr(img, "get_pixel_array"):
                    try:
                        img = img.get_pixel_array()
                        img_type = type(img)
                        logger.debug(
                            f"Extracted pixel array using get_pixel_array(), type: {img_type}"
                        )
                    except Exception as e:
                        logger.warning(f"get_pixel_array() failed: {e}")
                        img = None

                # Fallback to to_bytearray() if get_pixel_array didn't work or didn't exist
                # Need to get the original Image object - img might be None or already converted
                original_img = frame.pixels  # Get the original Image object
                if img is None or not hasattr(img, "shape"):
                    if hasattr(original_img, "to_bytearray"):
                        try:
                            import numpy as np

                            # to_bytearray() might return a list, tuple, or bytes directly
                            byte_result = original_img.to_bytearray()
                            logger.debug(f"to_bytearray() returned type: {type(byte_result)}")

                            # Handle different return types
                            byte_data = None
                            format_str = None

                            if isinstance(byte_result, tuple):
                                tuple_len = len(byte_result)
                                logger.debug(
                                    f"to_bytearray() returned tuple with length: {tuple_len}"
                                )
                                if len(byte_result) >= 1:
                                    byte_data = byte_result[0]
                                    format_str = byte_result[1] if len(byte_result) > 1 else None
                            elif isinstance(byte_result, list):
                                list_len = len(byte_result)
                                logger.debug(
                                    f"to_bytearray() returned list with length: {list_len}"
                                )
                                # List might be [byte_data, format] or just [byte_data]
                                if len(byte_result) >= 1:
                                    byte_data = byte_result[0]
                                    format_str = byte_result[1] if len(byte_result) > 1 else None
                                else:
                                    logger.warning("to_bytearray() returned empty list")
                                    return
                            elif isinstance(byte_result, bytes | bytearray):
                                logger.debug("to_bytearray() returned bytes/bytearray directly")
                                byte_data = byte_result
                            else:
                                result_type = type(byte_result)
                                logger.warning(
                                    f"to_bytearray() returned unexpected type: {result_type}"
                                )
                                return

                            byte_data_type = type(byte_data)
                            logger.debug(
                                f"Extracted byte_data type: {byte_data_type}, format: {format_str}"
                            )

                            # Convert byte_data to bytes if it's a list
                            if isinstance(byte_data, list):
                                list_len = len(byte_data)
                                logger.debug(f"Converting list to bytes, list length: {list_len}")
                                byte_data = bytes(byte_data)
                            elif not isinstance(byte_data, bytes | bytearray):
                                byte_data_type = type(byte_data)
                                logger.warning(
                                    f"byte_data is unexpected type: {byte_data_type}, "
                                    f"cannot convert"
                                )
                                return

                            byte_data_type = type(byte_data)
                            byte_data_len = len(byte_data)
                            logger.debug(
                                f"Final byte_data type: {byte_data_type}, length: {byte_data_len}"
                            )
                            logger.debug(
                                f"Frame dimensions: width={frame.width}, height={frame.height}"
                            )

                            # Use dimensions from frame (already extracted in video_player.py)
                            # Reshape to (height, width, channels) - assume RGB (3 channels)
                            expected_bytes = frame.width * frame.height * 3
                            actual_bytes = len(byte_data)
                            logger.debug(
                                f"Expected bytes for RGB: {expected_bytes}, "
                                f"actual bytes: {actual_bytes}"
                            )

                            if actual_bytes >= expected_bytes:
                                img = np.frombuffer(byte_data, dtype=np.uint8).reshape(
                                    (frame.height, frame.width, 3)
                                )
                                logger.debug(
                                    f"Converted Image to numpy array using to_bytearray(), "
                                    f"shape: {img.shape}"
                                )
                            else:
                                logger.warning(
                                    f"Byte data length mismatch: expected {expected_bytes}, "
                                    f"got {actual_bytes}"
                                )
                                return
                        except Exception as e:
                            logger.warning(f"to_bytearray() failed: {e}", exc_info=True)
                            return
                    else:
                        available_methods = [m for m in dir(original_img) if not m.startswith("_")]
                        methods_preview = available_methods[:15]
                        logger.warning(
                            f"ffpyplayer Image has no to_bytearray() method. "
                            f"Available: {methods_preview}"
                        )
                        return

            # Handle case where pixels might still be a tuple (from ffpyplayer)
            elif isinstance(img, tuple):
                tuple_len = len(img)
                tuple_types = [type(x) for x in img]
                logger.debug(
                    f"Frame pixels is a tuple with length {tuple_len}. Types: {tuple_types}"
                )
                if len(img) >= 1:
                    # ffpyplayer might return (pixel_data, format_string) or similar
                    # Try to find the numpy array in the tuple
                    for idx, item in enumerate(img):
                        if hasattr(item, "shape"):
                            logger.debug(f"Found numpy array at tuple index {idx}")
                            img = item
                            break
                    else:
                        # No numpy array found, use first element
                        logger.debug("No numpy array found in tuple, using first element")
                        img = img[0]
                else:
                    logger.warning("Empty tuple in frame.pixels, skipping frame")
                    return

            if hasattr(img, "shape"):
                height, width = img.shape[:2]
                logger.debug(f"Converting frame: {width}x{height}, shape: {img.shape}")

                # Convert numpy array to QImage
                # ffpyplayer typically uses RGB format
                if len(img.shape) == 3:
                    bytes_per_line = width * 3
                    # Ensure we have contiguous array for QImage
                    if not img.flags["C_CONTIGUOUS"]:
                        img = np.ascontiguousarray(img)

                    # Convert numpy array to bytes for QImage
                    # QImage constructor expects bytes, not numpy array buffer
                    img_bytes = img.tobytes()
                    qimage = QImage(
                        img_bytes, width, height, bytes_per_line, QImage.Format.Format_RGB888
                    )
                    if qimage.isNull():
                        logger.error("Failed to create QImage from frame data")
                        return

                    pixmap = QPixmap.fromImage(qimage)
                    if pixmap.isNull():
                        logger.error("Failed to create QPixmap from QImage")
                        return

                    scaled_pixmap = pixmap.scaled(
                        self.video_label.size(),
                        aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                        transformMode=Qt.TransformationMode.SmoothTransformation,
                    )
                    self.video_label.setPixmap(scaled_pixmap)

                    # Hide status/error labels when we have video
                    if self.error_label.isVisible():
                        self.error_label.hide()
                    self.video_label.show()

                    # Log first successful frame
                    if not hasattr(self, "_first_frame_shown"):
                        logger.info("First frame displayed successfully")
                        self._first_frame_shown = True
                else:
                    logger.warning(f"Unexpected image shape: {img.shape}, expected 3 dimensions")
            else:
                img_type = type(img)
                attrs = dir(img)[:10] if hasattr(img, "__dict__") else "N/A"
                logger.warning(
                    f"Frame pixels object has no 'shape' attribute: {img_type}. "
                    f"Attributes: {attrs}"
                )
        except Exception as e:
            logger.warning(f"Error updating frame: {e}", exc_info=True)

    def closeEvent(self, event: "QCloseEvent | None") -> None:  # noqa: N802
        """Handle window close event.

        Args:
            event: Qt close event

        Behavior:
            - Saves current window dimensions to configuration file (FR-006)
            - Stops video playback
            - Releases resources
            - Closes window

        Side Effects:
            - Configuration file updated with new dimensions
            - Video player stopped
            - Window closed
        """
        logger.info(f"Closing video window for feed: {self.feed_name}")

        # Save window dimensions
        try:
            from pick_a_zoo.core.feed_manager import update_feed_window_size

            update_feed_window_size(self.feed_name, self._current_width, self._current_height)
            logger.debug(f"Saved window dimensions: {self._current_width}x{self._current_height}")
        except Exception as e:
            logger.warning(f"Failed to save window dimensions: {e}", exc_info=True)

        # Stop video player
        if self._player:
            self._player.stop()
            self._player = None

        # Stop frame timer
        if hasattr(self, "_frame_timer"):
            self._frame_timer.stop()

        if event:
            event.accept()

    def resizeEvent(self, event: "QResizeEvent | None") -> None:  # noqa: N802
        """Handle window resize event.

        Args:
            event: Qt resize event

        Behavior:
            - Updates video display area to match new window size
            - Tracks new dimensions for saving on close
            - Debounces resize events (saves after 500ms of no resize)

        Side Effects:
            - Video display area resized
            - Dimensions tracked for persistence
        """
        if event:
            size = event.size()
            self._current_width = size.width()
            self._current_height = size.height()

        # Debounce resize events (will save on close)
        # For now, just track dimensions - saving happens on close

    def close(self) -> None:
        """Close the video window."""
        self._window.close()

    def _show_status(self, message: str) -> None:
        """Display a status message in the video window.

        Args:
            message: Status message to display
        """
        logger.info(f"Showing status: {message}")
        self.error_label.setText(message)
        self.error_label.setStyleSheet(
            "background-color: rgba(0, 0, 0, 200); color: white; font-size: 14px; padding: 20px;"
        )
        self.error_label.show()
        self.video_label.hide()

    def display_error(self, message: str) -> None:
        """Display an error message in the video window.

        Args:
            message: User-friendly error message to display

        Behavior:
            - Shows error message as QLabel overlay in window
            - Error message is visible and clear
            - Window remains closable (FR-012)

        Side Effects:
            - Error message displayed in window
            - Logs error display via structured logging
        """
        logger.error(f"Displaying error in video window: {message}")
        self.error_label.setText(f"Error: {message}")
        self.error_label.setStyleSheet(
            "background-color: rgba(200, 0, 0, 200); color: white; font-size: 14px; padding: 20px;"
        )
        self.error_label.show()
        self.video_label.hide()
