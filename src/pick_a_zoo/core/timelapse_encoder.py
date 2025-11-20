"""Timelapse encoder library for creating timelapse videos from video feeds.

This module follows the library-first architecture principle and is independently testable.
It provides functionality to capture frames from video feeds and encode them into
timelapse videos at 5x speed.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

import imageio
import numpy as np
from loguru import logger

if TYPE_CHECKING:
    pass


class TimelapseEncoderError(Exception):
    """Base exception for timelapse encoder errors."""

    def __init__(self, message: str, error_type: str = "unknown") -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            error_type: Error category (e.g., "encoding", "disk_space", "invalid_frame")
        """
        self.message = message
        self.error_type = error_type
        super().__init__(self.message)


class RecordingInProgressError(TimelapseEncoderError):
    """Raised when attempting to start a recording while one is already active."""

    def __init__(self, message: str = "A recording is already in progress") -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
        """
        super().__init__(message, error_type="recording_in_progress")


class NoRecordingError(TimelapseEncoderError):
    """Raised when attempting to perform recording operations when no recording is active."""

    def __init__(self, message: str = "No recording is currently in progress") -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
        """
        super().__init__(message, error_type="no_recording")


class EncodingError(TimelapseEncoderError):
    """Raised when video encoding fails."""

    def __init__(
        self,
        message: str,
        error_type: str = "codec_error",
    ) -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
            error_type: Error category ("disk_full", "codec_error", "invalid_frames")
        """
        super().__init__(message, error_type=error_type)


class DiskSpaceError(TimelapseEncoderError):
    """Raised when insufficient disk space is detected."""

    def __init__(self, message: str = "Insufficient disk space available") -> None:
        """Initialize the exception.

        Args:
            message: Human-readable error message
        """
        super().__init__(message, error_type="disk_space")


class TimelapseEncoder:
    """Timelapse encoder for creating timelapse videos from video feeds."""

    def __init__(self, output_directory: Path | None = None) -> None:
        """Initialize timelapse encoder with output directory.

        Args:
            output_directory: Directory where timelapse videos will be saved.
                If None, uses .pickazoo/timelapses/ directory in current working directory.

        Raises:
            ValueError: If output_directory is provided but not writable
            OSError: If output_directory cannot be created

        Side Effects:
            Creates output directory if it doesn't exist
            Logs initialization via structured logging
        """
        if output_directory is None:
            # Use .pickazoo directory in current working directory (same pattern as feeds.yaml)
            app_data_dir = Path.cwd() / ".pickazoo"
            self._output_directory = app_data_dir / "timelapses"
        else:
            self._output_directory = Path(output_directory)
            # Validate writability if directory exists
            if self._output_directory.exists() and not os.access(self._output_directory, os.W_OK):
                raise ValueError(f"Output directory is not writable: {self._output_directory}")

        # Create directory if it doesn't exist
        try:
            self._output_directory.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            logger.error(f"Failed to create output directory: {e}")
            raise

        # Recording state
        self._is_recording = False
        self._feed_name: str | None = None
        self._source_fps: float = 30.0
        self._output_fps: float = 150.0
        self._frames: list[np.ndarray] = []
        self._start_time: datetime | None = None

        logger.info(f"TimelapseEncoder initialized with output directory: {self._output_directory}")

    def start_recording(self, feed_name: str, source_fps: float = 30.0) -> None:
        """Start a new timelapse recording session.

        Args:
            feed_name: Name of the feed being recorded (used for filename)
            source_fps: Source video frame rate in frames per second (default: 30.0)

        Raises:
            ValueError: If feed_name is empty or invalid
            RecordingInProgressError: If a recording is already in progress
            DiskSpaceError: If insufficient disk space (checked before starting)

        Behavior:
            - Validates feed_name and source_fps
            - Checks available disk space
            - Initializes frame buffer
            - Sets recording state to active
            - Calculates output fps (source_fps * 5)

        Side Effects:
            Recording state set to active
            Frame buffer initialized
            Logs recording start via structured logging
        """
        if not feed_name or not isinstance(feed_name, str) or not feed_name.strip():
            raise ValueError("feed_name must be a non-empty string")

        if self._is_recording:
            raise RecordingInProgressError()

        # Check disk space (minimum 100MB free)
        free_space = shutil.disk_usage(self._output_directory).free
        min_required = 100 * 1024 * 1024  # 100MB
        if free_space < min_required:
            free_mb = free_space / (1024 * 1024)
            required_mb = min_required / (1024 * 1024)
            raise DiskSpaceError(
                f"Insufficient disk space: {free_mb:.1f}MB available, {required_mb:.1f}MB required"
            )

        # Validate source_fps
        if source_fps <= 0:
            raise ValueError("source_fps must be positive")

        self._feed_name = feed_name.strip()
        self._source_fps = source_fps
        self._output_fps = source_fps * 5.0
        self._frames = []
        self._start_time = datetime.now()
        self._is_recording = True

        logger.info(
            f"Started timelapse recording: feed='{self._feed_name}', "
            f"source_fps={self._source_fps:.1f}, output_fps={self._output_fps:.1f}"
        )

    def capture_frame(self, frame: np.ndarray) -> None:
        """Capture a frame from the video feed and add it to the recording buffer.

        Args:
            frame: Video frame as numpy array with shape (height, width, 3) for RGB

        Raises:
            NoRecordingError: If no recording is in progress
            ValueError: If frame is invalid (wrong shape, wrong dtype, etc.)

        Behavior:
            - Validates frame format
            - Adds frame to in-memory buffer
            - Tracks frame count and timestamps

        Side Effects:
            Frame added to buffer
            Memory usage increased
            Logs frame capture (debug level)
        """
        if not self._is_recording:
            raise NoRecordingError()

        # Validate frame
        if not isinstance(frame, np.ndarray):
            raise ValueError("frame must be a numpy array")
        if frame.ndim != 3:
            raise ValueError(f"frame must be 3D array (height, width, channels), got {frame.ndim}D")
        if frame.shape[2] != 3:
            raise ValueError(f"frame must have 3 channels (RGB), got {frame.shape[2]} channels")
        if frame.dtype != np.uint8:
            raise ValueError(f"frame must be uint8 dtype, got {frame.dtype}")

        # Add frame to buffer
        self._frames.append(frame.copy())
        logger.debug(f"Captured frame {len(self._frames)}")

    def stop_recording(self) -> Path:
        """Stop recording and encode captured frames into a video file.

        Returns:
            Path: Path to the saved timelapse video file

        Raises:
            NoRecordingError: If no recording is in progress
            ValueError: If no frames were captured
            EncodingError: If video encoding fails or file cannot be written

        Behavior:
            - Stops frame capture
            - Encodes all buffered frames into MP4 video at 5x speed
            - Saves video file with timestamp-based filename
            - Clears frame buffer
            - Sets recording state to idle

        Side Effects:
            Video file created on disk
            Frame buffer cleared
            Recording state set to idle
            Logs encoding completion via structured logging
        """
        if not self._is_recording:
            raise NoRecordingError()

        if len(self._frames) == 0:
            self._is_recording = False
            self._frames = []
            raise ValueError("No frames captured, cannot create video")

        # Generate filename
        video_path = self._generate_filename()

        try:
            # Encode video using imageio-ffmpeg
            self._encode_video(video_path)
        except Exception as e:
            self._is_recording = False
            self._frames = []
            logger.error(f"Failed to encode video: {e}")
            raise EncodingError(f"Video encoding failed: {e}", error_type="codec_error") from e

        # Clear state
        frame_count = len(self._frames)
        self._is_recording = False
        self._frames = []

        logger.info(f"Timelapse saved: {video_path} ({frame_count} frames)")
        return video_path

    def is_recording(self) -> bool:
        """Check if a recording is currently in progress.

        Returns:
            bool: True if recording is active, False otherwise

        Side Effects:
            None (read-only operation)
        """
        return self._is_recording

    def get_frame_count(self) -> int:
        """Get the number of frames captured in the current recording.

        Returns:
            int: Number of frames in buffer (0 if not recording)

        Raises:
            NoRecordingError: If no recording is in progress

        Side Effects:
            None (read-only operation)
        """
        if not self._is_recording:
            raise NoRecordingError()
        return len(self._frames)

    def cancel_recording(self) -> None:
        """Cancel the current recording without saving.

        Raises:
            NoRecordingError: If no recording is in progress

        Behavior:
            - Stops frame capture
            - Clears frame buffer
            - Sets recording state to idle
            - Does not create video file

        Side Effects:
            Frame buffer cleared
            Recording state set to idle
            Logs cancellation via structured logging
        """
        if not self._is_recording:
            raise NoRecordingError()

        frame_count = len(self._frames)
        self._is_recording = False
        self._frames = []
        logger.info(f"Recording cancelled ({frame_count} frames discarded)")

    def _generate_filename(self) -> Path:
        """Generate timestamp-based filename for timelapse video.

        Returns:
            Path: Full path to video file with timestamp-based name

        Format: <sanitized-feed-name>-YYYYMMDD-HHMMSS.mp4
        """
        if not self._feed_name:
            raise ValueError("feed_name not set")

        # Sanitize feed name: spaces -> hyphens, remove special chars
        sanitized_name = "".join(c if c.isalnum() or c == " " else "-" for c in self._feed_name)
        sanitized_name = "-".join(sanitized_name.split())  # Replace spaces with hyphens
        sanitized_name = sanitized_name.strip("-")  # Remove leading/trailing hyphens

        # Generate timestamp
        if self._start_time:
            timestamp = self._start_time.strftime("%Y%m%d-%H%M%S")
        else:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

        # Construct filename
        filename = f"{sanitized_name}-{timestamp}.mp4"
        video_path = self._output_directory / filename

        # Handle collisions (unlikely but possible)
        counter = 1
        while video_path.exists():
            filename = f"{sanitized_name}-{timestamp}-{counter}.mp4"
            video_path = self._output_directory / filename
            counter += 1

        return video_path

    def _encode_video(self, output_path: Path) -> None:
        """Encode captured frames into MP4 video at 5x speed.

        Args:
            output_path: Path where video file will be saved

        Raises:
            EncodingError: If encoding fails

        Behavior:
            - Encodes frames using imageio-ffmpeg
            - Sets output fps to 5x source fps
            - Uses H.264 codec for compatibility
        """
        if len(self._frames) == 0:
            raise ValueError("No frames to encode")

        try:
            # Use imageio with ffmpeg plugin for MP4 encoding
            # imageio-ffmpeg plugin is automatically used when available
            writer = imageio.get_writer(
                str(output_path),
                fps=self._output_fps,
                codec="libx264",
                quality=8,  # Good quality (0-10 scale)
                pixelformat="yuv420p",  # Compatible format
            )

            # Write all frames
            for frame in self._frames:
                writer.append_data(frame)

            writer.close()
        except Exception as e:
            logger.error(f"Video encoding error: {e}")
            # Clean up partial file if it exists
            if output_path.exists():
                try:
                    output_path.unlink()
                except Exception:
                    pass
            raise EncodingError(f"Failed to encode video: {e}", error_type="codec_error") from e

