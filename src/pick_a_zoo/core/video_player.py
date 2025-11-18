"""Video player library for loading and playing video streams.

This module follows the library-first architecture principle and is independently testable.
It wraps ffpyplayer to provide a clean interface for loading streams, controlling playback,
handling errors, and extracting frames.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from typing import Any


# Window dimension constants
DEFAULT_WINDOW_WIDTH = 1280
DEFAULT_WINDOW_HEIGHT = 720
MIN_WINDOW_WIDTH = 320
MIN_WINDOW_HEIGHT = 240
MAX_WINDOW_WIDTH = 7680
MAX_WINDOW_HEIGHT = 4320


@dataclass
class VideoFrame:
    """Represents a single video frame."""

    pixels: "Any"  # Pixel data from ffpyplayer
    width: int
    height: int
    timestamp: float


class VideoPlayerError(Exception):
    """Base exception for video player errors."""

    def __init__(self, message: str, error_type: str = "unknown") -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            error_type: Error category (e.g., "network", "codec", "stream")
        """
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)


class StreamLoadError(VideoPlayerError):
    """Raised when stream cannot be loaded.

    Error Types:
        - "network": Network connectivity issue
        - "unavailable": Stream URL returns 404 or similar
        - "timeout": Connection timeout
        - "invalid_format": Stream format not supported
    """

    def __init__(self, message: str, error_type: str = "unavailable") -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            error_type: Error category (default: "unavailable")
        """
        super().__init__(message, error_type)


class VideoPlayer:
    """Main class for video playback operations."""

    def __init__(self, stream_url: str) -> None:
        """Initialize video player with a stream URL.

        Args:
            stream_url: URL of the video stream to play (supports m3u8, mp4, webm, rtsp, etc.)

        Raises:
            ValueError: If stream_url is empty or invalid format
            VideoPlayerError: If initialization fails

        Side Effects:
            None (lazy initialization, stream not loaded until load() called)
        """
        if not stream_url or not isinstance(stream_url, str):
            raise ValueError("stream_url must be a non-empty string")

        self.stream_url = stream_url.strip()
        if not self.stream_url:
            raise ValueError("stream_url cannot be empty")

        logger.debug(f"VideoPlayer initialized with URL: {self.stream_url}")

        # Internal state (will be initialized in load())
        self._player: Any = None
        self._is_playing = False
        self._error: VideoPlayerError | None = None

    def load(self) -> None:
        """Load the video stream and prepare for playback.

        Returns:
            None

        Behavior:
            - Attempts to connect to stream URL
            - Validates stream format and accessibility
            - Prepares video decoder and buffers
            - Raises error if stream cannot be loaded

        Raises:
            StreamLoadError: If stream URL is inaccessible, invalid format, or network error
            VideoPlayerError: If video player initialization fails

        Side Effects:
            - Network I/O (stream connection)
            - Logs loading process via structured logging
        """
        try:
            from ffpyplayer.player import MediaPlayer

            logger.info(f"Loading stream: {self.stream_url}")
            self._error = None

            # Create MediaPlayer instance
            # ffpyplayer.MediaPlayer handles stream loading
            self._player = MediaPlayer(self.stream_url)
            logger.debug("Stream loaded successfully")
        except ImportError as e:
            error_msg = "ffpyplayer not available"
            logger.error(f"{error_msg}: {e}")
            self._error = VideoPlayerError(error_msg, "initialization")
            raise VideoPlayerError(error_msg, "initialization") from e
        except Exception as e:
            error_msg = f"Failed to load stream: {str(e)}"
            logger.error(error_msg, exc_info=True)
            # Determine error type
            error_type = "network"
            if "404" in str(e) or "not found" in str(e).lower():
                error_type = "unavailable"
            elif "timeout" in str(e).lower():
                error_type = "timeout"
            elif "format" in str(e).lower() or "codec" in str(e).lower():
                error_type = "invalid_format"

            self._error = StreamLoadError(error_msg, error_type)
            raise StreamLoadError(error_msg, error_type) from e

    def play(self) -> None:
        """Start video playback.

        Returns:
            None

        Behavior:
            - Begins decoding and displaying video frames
            - Playback starts automatically after load
            - If already playing, has no effect

        Raises:
            VideoPlayerError: If playback cannot start (stream not loaded, codec error, etc.)

        Side Effects:
            - Video frames decoded and available for display
            - Logs playback events via structured logging
        """
        if self._player is None:
            raise VideoPlayerError("Stream not loaded. Call load() first.", "playback")

        if self._is_playing:
            logger.debug("Already playing, ignoring play() call")
            return

        try:
            # ffpyplayer MediaPlayer starts playing automatically when created
            # We just need to mark it as playing
            self._is_playing = True
            self._error = None
            logger.info("Playback started")
        except Exception as e:
            error_msg = f"Failed to start playback: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self._error = VideoPlayerError(error_msg, "playback")
            self._is_playing = False
            raise VideoPlayerError(error_msg, "playback") from e

    def stop(self) -> None:
        """Stop video playback and release resources.

        Returns:
            None

        Behavior:
            - Stops decoding and frame generation
            - Releases video decoder and buffers
            - Cleans up network connections

        Side Effects:
            - Resources released
            - Logs stop event via structured logging
        """
        if self._player is None:
            return

        try:
            # Close the MediaPlayer to release resources
            if hasattr(self._player, "close"):
                self._player.close()
            self._is_playing = False
            self._player = None
            logger.info("Playback stopped and resources released")
        except Exception as e:
            logger.warning(f"Error stopping playback: {e}", exc_info=True)
            # Still mark as stopped even if cleanup had errors
            self._is_playing = False
            self._player = None

    def get_frame(self) -> VideoFrame | None:
        """Get the next video frame for display.

        Returns:
            VideoFrame object with frame data, or None if no frame available

        Behavior:
            - Returns decoded video frame if available
            - Returns None if playback stopped or no frame ready
            - Frame contains pixel data and timestamp

        Side Effects:
            None (read-only operation)
        """
        if self._player is None or not self._is_playing:
            return None

        try:
            # Get frame from MediaPlayer
            # ffpyplayer returns (frame, val) where val is the timestamp
            frame_data = self._player.get_frame()
            if frame_data is None:
                return None

            # ffpyplayer returns (img, pts) tuple
            # img can be a numpy array, or sometimes a tuple (data, format)
            # pts is presentation timestamp
            img, pts = frame_data

            if img is None:
                return None

            # Handle different ffpyplayer return formats
            # ffpyplayer returns (img, pts) where img can be:
            # - A numpy array directly
            # - An ffpyplayer.pic.Image object
            # - A tuple (pixel_data, format_string) - where pixel_data might be an Image object
            pixel_data = img

            # First check if img is a tuple (ffpyplayer sometimes wraps Image in tuple)
            if isinstance(img, tuple):
                types_list = [type(x).__name__ for x in img]
                logger.info(f"Frame image is a tuple with length: {len(img)}, types: {types_list}")
                if len(img) >= 1:
                    img = img[0]  # Extract the actual image object from tuple
                    logger.info(f"Extracted from tuple: type={type(img).__name__}")
                else:
                    logger.warning(f"Unexpected tuple format from ffpyplayer: {img}")
                    return None

            # Now check if img is an ffpyplayer.pic.Image object
            # These objects need special handling to extract pixel data
            img_type_name = type(img).__name__
            img_type_str = str(type(img))
            logger.info(f"Processing frame image type: {img_type_name}, full type: {img_type_str}")

            if img_type_name == "Image" or "ffpyplayer" in img_type_str:
                # Log available methods for debugging
                available_methods = [m for m in dir(img) if not m.startswith("_")]
                methods_preview = available_methods[:20]
                logger.info(f"ffpyplayer Image detected! Available methods: {methods_preview}")

                # ffpyplayer.pic.Image API:
                # - get_size() returns (width, height) tuple
                # - to_bytearray() returns (byte_data, format) tuple
                # - get_pixel_array() returns numpy array directly

                # Try get_pixel_array first (returns numpy array directly)
                if hasattr(img, "get_pixel_array"):
                    try:
                        pixel_data = img.get_pixel_array()
                        pixel_type = type(pixel_data)
                        logger.debug(
                            f"Extracted pixel array using get_pixel_array(), type: {pixel_type}"
                        )
                    except Exception as e:
                        logger.warning(f"get_pixel_array() failed: {e}")
                        pixel_data = None

                # Fallback to to_bytearray() if get_pixel_array didn't work
                if pixel_data is None or not hasattr(pixel_data, "shape"):
                    if hasattr(img, "to_bytearray"):
                        try:
                            import numpy as np

                            # to_bytearray() might return a list, tuple, or bytes directly
                            byte_result = img.to_bytearray()
                            result_type = type(byte_result)
                            logger.debug(
                                f"to_bytearray() returned type: {result_type}, "
                                f"value type info: {result_type.__name__}"
                            )

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
                                    byte_data_type = type(byte_data)
                                    logger.debug(
                                        f"Extracted from tuple: byte_data type: {byte_data_type}, "
                                        f"format: {format_str}"
                                    )
                            elif isinstance(byte_result, list):
                                list_len = len(byte_result)
                                logger.debug(
                                    f"to_bytearray() returned list with length: {list_len}"
                                )
                                # List might be [byte_data, format] or just [byte_data]
                                if len(byte_result) >= 1:
                                    byte_data = byte_result[0]
                                    format_str = byte_result[1] if len(byte_result) > 1 else None
                                    byte_data_type = type(byte_data)
                                    logger.debug(
                                        f"Extracted from list: byte_data type: {byte_data_type}, "
                                        f"format: {format_str}"
                                    )
                                else:
                                    logger.warning("to_bytearray() returned empty list")
                                    return None
                            elif isinstance(byte_result, (bytes, bytearray)):
                                logger.debug("to_bytearray() returned bytes/bytearray directly")
                                byte_data = byte_result
                            else:
                                result_type = type(byte_result)
                                logger.warning(
                                    f"to_bytearray() returned unexpected type: {result_type}"
                                )
                                return None

                            # Convert byte_data to bytes if it's a list
                            if isinstance(byte_data, list):
                                list_len = len(byte_data)
                                logger.debug(f"Converting list to bytes, list length: {list_len}")
                                byte_data = bytes(byte_data)
                            elif not isinstance(byte_data, (bytes, bytearray)):
                                byte_data_type = type(byte_data)
                                logger.warning(
                                    f"byte_data is unexpected type: {byte_data_type}, "
                                    f"cannot convert"
                                )
                                return None

                            byte_data_type = type(byte_data)
                            byte_data_len = (
                                len(byte_data) if hasattr(byte_data, "__len__") else "N/A"
                            )
                            logger.debug(
                                f"Final byte_data type: {byte_data_type}, length: {byte_data_len}"
                            )

                            # Get dimensions from Image object
                            if hasattr(img, "get_size"):
                                size_result = img.get_size()
                                size_result_type = type(size_result)
                                logger.debug(
                                    f"get_size() returned: {size_result}, type: {size_result_type}"
                                )

                                if isinstance(size_result, tuple) and len(size_result) >= 2:
                                    width, height = size_result[0], size_result[1]
                                    logger.debug(
                                        f"Extracted dimensions: width={width}, height={height}"
                                    )

                                    # Calculate expected bytes for RGB (3 bytes per pixel)
                                    expected_bytes = width * height * 3
                                    actual_bytes = len(byte_data)
                                    logger.debug(
                                        f"Expected bytes for RGB: {expected_bytes}, "
                                        f"actual bytes: {actual_bytes}"
                                    )

                                    if actual_bytes >= expected_bytes:
                                        # Assume RGB format (3 bytes per pixel)
                                        pixel_data = np.frombuffer(
                                            byte_data, dtype=np.uint8
                                        ).reshape((height, width, 3))
                                        logger.debug(
                                            f"Created numpy array from bytearray: "
                                            f"shape={pixel_data.shape}, dtype={pixel_data.dtype}"
                                        )
                                    else:
                                        logger.warning(
                                            f"Byte data length mismatch: "
                                            f"expected {expected_bytes}, got {actual_bytes}"
                                        )
                                        return None
                                else:
                                    size_result_type = type(size_result)
                                    logger.warning(
                                        f"get_size() returned unexpected format: {size_result}, "
                                        f"type: {size_result_type}"
                                    )
                                    return None
                            else:
                                methods_preview = available_methods[:15]
                                logger.warning(
                                    f"ffpyplayer Image has no get_size() method. "
                                    f"Available methods: {methods_preview}"
                                )
                                return None
                        except Exception as e:
                            logger.warning(f"to_bytearray() failed: {e}", exc_info=True)
                            return None
                    else:
                        methods_preview = available_methods[:10]
                        logger.warning(
                            f"ffpyplayer Image has no to_bytearray() method. "
                            f"Available: {methods_preview}"
                        )
                        return None

            # Extract dimensions from image
            # ffpyplayer image format varies, but typically has shape attribute
            if hasattr(pixel_data, "shape"):
                height, width = pixel_data.shape[:2]
            else:
                # Fallback: try to get size from image object (only if not a tuple)
                width, height = 1280, 720  # Default

                # Try to get size from original img object (if it's an ffpyplayer Image)
                if not isinstance(img, tuple):
                    if hasattr(img, "get_size"):
                        try:
                            size_result = img.get_size()
                            if isinstance(size_result, tuple) and len(size_result) >= 2:
                                width, height = size_result[0], size_result[1]
                        except Exception:
                            pass
                    elif hasattr(img, "size") and not isinstance(img.size, int):
                        try:
                            size_result = img.size
                            if isinstance(size_result, tuple) and len(size_result) >= 2:
                                width, height = size_result[0], size_result[1]
                        except Exception:
                            pass

                # Try pixel_data only if it's not a numpy array (which we already checked)
                # Use type check to exclude numpy arrays
                import numpy as np

                if (
                    not isinstance(pixel_data, tuple)
                    and not isinstance(pixel_data, np.ndarray)
                    and not hasattr(pixel_data, "shape")
                ):
                    if hasattr(pixel_data, "get_size"):
                        try:
                            size_result = pixel_data.get_size()  # type: ignore[attr-defined, unused-ignore]
                            if isinstance(size_result, tuple) and len(size_result) >= 2:
                                width, height = size_result[0], size_result[1]
                        except Exception:
                            pass

                # If we still have defaults, log a warning
                if width == 1280 and height == 720:
                    pixel_data_type = type(pixel_data)
                    logger.warning(
                        f"Cannot determine dimensions from pixel data type: {pixel_data_type}"
                    )

            return VideoFrame(pixels=pixel_data, width=width, height=height, timestamp=pts)
        except Exception as e:
            logger.warning(f"Error getting frame: {e}", exc_info=True)
            # Check if this is a connection loss
            if "connection" in str(e).lower() or "network" in str(e).lower():
                self._error = StreamLoadError("Connection lost during playback", "network")
                self._is_playing = False
            return None

    def is_playing(self) -> bool:
        """Check if video is currently playing.

        Returns:
            True if playing, False otherwise
        """
        return self._is_playing

    def get_error(self) -> VideoPlayerError | None:
        """Get the last error that occurred, if any.

        Returns:
            VideoPlayerError object if error occurred, None otherwise

        Behavior:
            - Returns most recent error
            - Error cleared when new operation succeeds
        """
        return self._error
