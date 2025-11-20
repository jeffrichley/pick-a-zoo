# Quick Start: Create Timelapse Video from Active Feed

**Feature**: 005-create-timelapse
**Date**: 2025-11-20

## Overview

This guide provides a quick start for implementing the "Create Timelapse Video from Active Feed" feature. The feature enables users to click a button in the video window to create condensed video recordings at 5x normal speed from the currently playing feed.

## Architecture Overview

The feature consists of two main components:

1. **Timelapse Encoder Library** (`core/timelapse_encoder.py`): Standalone library for frame capture, buffering, and video encoding at 5x speed
2. **Video Window Extension** (`gui/video_window.py`): Extended with timelapse button and recording lifecycle management

## Implementation Steps

### Step 1: Add Dependency

Add `imageio-ffmpeg` to `pyproject.toml`:

```toml
dependencies = [
    # ... existing dependencies ...
    "imageio-ffmpeg>=2.0.0",  # Video encoding for timelapse
]
```

### Step 2: Create Timelapse Encoder Library

Create `src/pick_a_zoo/core/timelapse_encoder.py`:

```python
"""Timelapse encoder library for creating 5x speed videos from frames."""

from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import numpy as np
from loguru import logger
import platformdirs

try:
    import imageio
    import imageio_ffmpeg
except ImportError:
    imageio = None
    imageio_ffmpeg = None


class TimelapseEncoderError(Exception):
    """Base exception for timelapse encoder errors."""
    pass


class TimelapseEncoder:
    """Main class for timelapse recording and encoding."""

    def __init__(self, output_directory: Path | None = None) -> None:
        """Initialize encoder with output directory."""
        if output_directory is None:
            app_dir = Path(platformdirs.user_data_dir('pick-a-zoo'))
            output_directory = app_dir / 'timelapses'

        output_directory.mkdir(parents=True, exist_ok=True)
        self.output_directory = output_directory
        self._frames: list[np.ndarray] = []
        self._is_recording = False
        self._feed_name = ""
        self._source_fps = 30.0
        self._output_fps = 150.0  # 5x speed

    def start_recording(self, feed_name: str, source_fps: float = 30.0) -> None:
        """Start a new timelapse recording."""
        if self._is_recording:
            raise RuntimeError("Recording already in progress")

        if not feed_name:
            raise ValueError("feed_name must be non-empty")

        # Check disk space (simplified - implement proper check)
        # ... disk space check ...

        self._feed_name = feed_name
        self._source_fps = source_fps
        self._output_fps = source_fps * 5.0
        self._frames = []
        self._is_recording = True
        logger.info(f"Started timelapse recording: {feed_name} at {source_fps}fps")

    def capture_frame(self, frame: np.ndarray) -> None:
        """Capture a frame for timelapse."""
        if not self._is_recording:
            raise RuntimeError("No recording in progress")

        # Validate frame shape
        if len(frame.shape) != 3 or frame.shape[2] != 3:
            raise ValueError("Frame must be RGB array with shape (height, width, 3)")

        self._frames.append(frame.copy())

    def stop_recording(self) -> Path:
        """Stop recording and encode video."""
        if not self._is_recording:
            raise RuntimeError("No recording in progress")

        if len(self._frames) == 0:
            raise ValueError("No frames captured")

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        sanitized_name = self._feed_name.replace(" ", "-").replace("/", "-")
        filename = f"{sanitized_name}-{timestamp}.mp4"
        output_path = self.output_directory / filename

        # Encode video
        try:
            self._encode_video(output_path)
        except Exception as e:
            logger.error(f"Encoding failed: {e}")
            raise

        # Cleanup
        self._frames = []
        self._is_recording = False

        logger.info(f"Timelapse saved: {output_path}")
        return output_path

    def _encode_video(self, output_path: Path) -> None:
        """Encode frames into MP4 video at 5x speed."""
        if imageio is None or imageio_ffmpeg is None:
            raise ImportError("imageio-ffmpeg not available")

        writer = imageio.get_writer(
            str(output_path),
            fps=self._output_fps,
            codec='libx264',
            format='mp4'
        )

        try:
            for frame in self._frames:
                writer.append_data(frame)
        finally:
            writer.close()

    def is_recording(self) -> bool:
        """Check if recording is active."""
        return self._is_recording
```

### Step 3: Extend Video Window

Update `src/pick_a_zoo/gui/video_window.py`:

```python
from pick_a_zoo.core.timelapse_encoder import TimelapseEncoder

class VideoWindow:
    def __init__(self, feed_name: str, stream_url: str, width: int = 1280, height: int = 720):
        # ... existing initialization ...

        # Timelapse recording state
        self.timelapse_encoder: TimelapseEncoder | None = None
        self.is_recording_timelapse = False

        # Create timelapse button
        self._setup_timelapse_button()

    def _setup_timelapse_button(self) -> None:
        """Create and configure timelapse button."""
        from PyQt6.QtWidgets import QPushButton

        self.timelapse_button = QPushButton("Start Timelapse")
        self.timelapse_button.clicked.connect(self._on_timelapse_button_clicked)
        # Add to layout (toolbar or overlay)

    def _on_timelapse_button_clicked(self) -> None:
        """Handle timelapse button click."""
        if self.is_recording_timelapse:
            self._stop_timelapse_recording()
        else:
            self._start_timelapse_recording()

    def _start_timelapse_recording(self) -> None:
        """Start timelapse recording."""
        if not self._player or not self._player.is_playing():
            self.display_error("Cannot create timelapse: video not playing")
            return

        try:
            self.timelapse_encoder = TimelapseEncoder()
            source_fps = 30.0  # Default or detect from player
            self.timelapse_encoder.start_recording(self.feed_name, source_fps)
            self.is_recording_timelapse = True
            self._update_timelapse_button_state()
            self._show_status("Recording timelapse...")
        except Exception as e:
            self.display_error(f"Failed to start recording: {e}")

    def _stop_timelapse_recording(self) -> None:
        """Stop timelapse recording and save."""
        if not self.timelapse_encoder:
            return

        try:
            video_path = self.timelapse_encoder.stop_recording()
            self._show_status(f"Timelapse saved: {video_path.name}")
            self.is_recording_timelapse = False
            self._update_timelapse_button_state()
        except Exception as e:
            self.display_error(f"Failed to save timelapse: {e}")
        finally:
            self.timelapse_encoder = None

    def _update_timelapse_button_state(self) -> None:
        """Update button visual state."""
        if self.is_recording_timelapse:
            self.timelapse_button.setText("Stop Timelapse")
            self.timelapse_button.setStyleSheet("background-color: red;")
        else:
            self.timelapse_button.setText("Start Timelapse")
            self.timelapse_button.setStyleSheet("")

    def _update_frame(self) -> None:
        """Extended to capture frames for timelapse."""
        # ... existing frame display code ...

        # Capture frame if recording
        if self.is_recording_timelapse and self.timelapse_encoder:
            try:
                # Convert displayed frame to numpy array
                frame_array = self._convert_frame_to_array(scaled_pixmap)
                self.timelapse_encoder.capture_frame(frame_array)
            except Exception as e:
                logger.warning(f"Failed to capture frame: {e}")

    def closeEvent(self, event: QCloseEvent | None) -> None:
        """Extended to stop recording on close."""
        if self.is_recording_timelapse:
            self._stop_timelapse_recording()
        # ... existing close code ...
```

## Testing Strategy

### Unit Tests

1. **test_timelapse_encoder.py**:
   - Test recording start/stop lifecycle
   - Test frame capture and buffering
   - Test video encoding at correct speed
   - Test error handling (disk space, encoding errors)
   - Test filename generation and uniqueness
   - Test directory creation

2. **test_video_window.py** (extend existing):
   - Test button creation and layout
   - Test button click handling
   - Test visual feedback updates
   - Test frame capture integration
   - Test error handling
   - Test window close with active recording

### Integration Tests

1. **test_video_window_integration.py** (extend existing):
   - Test end-to-end timelapse creation workflow
   - Test button-to-encoder integration
   - Test video file creation and playback
   - Test error scenarios (disk full, feed errors)

## Key Implementation Details

### Frame Capture

- Capture frames from VideoPlayer.get_frame() during normal playback
- Convert QPixmap/QImage to numpy array for encoder
- Handle frame format conversion (RGB, shape validation)

### Video Encoding

- Use imageio-ffmpeg with MP4/H.264 codec
- Set output fps = source_fps * 5 for 5x speed
- Encode all captured frames sequentially
- Handle encoding errors gracefully

### File Management

- Use platformdirs for cross-platform directory paths
- Create timelapses directory automatically
- Generate timestamp-based filenames for uniqueness
- Handle disk space errors before starting

### Button Integration

- Add button to video window layout (toolbar or overlay)
- Update button state based on recording status
- Provide visual feedback (text change, color change)
- Handle button clicks to start/stop recording

### Error Handling

- Check disk space before starting recording
- Handle encoding errors with user-friendly messages
- Save partial recordings on feed errors
- Allow user to dismiss errors and continue

## Dependencies

### New Dependencies

- `imageio-ffmpeg>=2.0.0`: Video encoding library

### Existing Dependencies Used

- `numpy`: Frame data manipulation
- `PyQt6`: GUI framework
- `platformdirs`: Directory path management
- `loguru`: Structured logging
- `pick_a_zoo.core.video_player`: Frame extraction

## Next Steps

1. Write unit tests first (TDD) for timelapse_encoder
2. Implement timelapse_encoder.py library
3. Extend video_window.py with button and recording logic
4. Write integration tests
5. Manual testing with real video feeds
6. Performance testing for long recordings

## References

- [Timelapse Encoder Contract](./contracts/timelapse-encoder.md)
- [Video Window Extension Contract](./contracts/video-window-extension.md)
- [Data Model](./data-model.md)
- [Research Findings](./research.md)
