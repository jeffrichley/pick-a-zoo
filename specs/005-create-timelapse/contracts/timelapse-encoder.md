# Timelapse Encoder Library Contract

**Module**: `pick_a_zoo.core.timelapse_encoder`
**Type**: Internal Library API
**Constitution**: Library-First Architecture (Principle II)

## Overview

The Timelapse Encoder library is a standalone, independently testable module that provides timelapse video creation functionality. It captures frames from an active video feed, buffers them in memory, and encodes them into a standard MP4 video file at 5x normal speed. The library is GUI-agnostic and can be used by any video display component.

## Interface

### `TimelapseEncoder`

Main class for timelapse recording and encoding operations.

#### `__init__(output_directory: Path | None = None) -> None`

Initialize timelapse encoder with output directory.

**Parameters**:
- `output_directory` (Path | None): Directory where timelapse videos will be saved. If None, uses platformdirs to get application data directory / timelapses.

**Raises**:
- `ValueError`: If output_directory is provided but not writable
- `OSError`: If output_directory cannot be created

**Side Effects**:
- Creates output directory if it doesn't exist
- Logs initialization via structured logging

**Example**:
```python
from pick_a_zoo.core.timelapse_encoder import TimelapseEncoder
from pathlib import Path

encoder = TimelapseEncoder()
# Uses default: platformdirs.user_data_dir('pick-a-zoo') / 'timelapses'
```

#### `start_recording(feed_name: str, source_fps: float = 30.0) -> None`

Start a new timelapse recording session.

**Parameters**:
- `feed_name` (str): Name of the feed being recorded (used for filename)
- `source_fps` (float): Source video frame rate in frames per second (default: 30.0)

**Raises**:
- `ValueError`: If feed_name is empty or invalid
- `RuntimeError`: If a recording is already in progress
- `OSError`: If insufficient disk space (checked before starting)

**Behavior**:
- Validates feed_name and source_fps
- Checks available disk space
- Initializes frame buffer
- Sets recording state to active
- Calculates output fps (source_fps * 5)

**Side Effects**:
- Recording state set to active
- Frame buffer initialized
- Logs recording start via structured logging

**Example**:
```python
encoder.start_recording("Panda Cam", source_fps=30.0)
# Output fps will be 150.0 (30 * 5)
```

#### `capture_frame(frame: numpy.ndarray) -> None`

Capture a frame from the video feed and add it to the recording buffer.

**Parameters**:
- `frame` (numpy.ndarray): Video frame as numpy array with shape (height, width, 3) for RGB

**Raises**:
- `RuntimeError`: If no recording is in progress
- `ValueError`: If frame is invalid (wrong shape, wrong dtype, etc.)

**Behavior**:
- Validates frame format
- Adds frame to in-memory buffer
- Tracks frame count and timestamps

**Side Effects**:
- Frame added to buffer
- Memory usage increased
- Logs frame capture (debug level)

**Example**:
```python
import numpy as np

# Frame from VideoPlayer.get_frame()
frame_array = np.array([...])  # Shape: (height, width, 3)
encoder.capture_frame(frame_array)
```

#### `stop_recording() -> Path`

Stop recording and encode captured frames into a video file.

**Returns**:
- `Path`: Path to the saved timelapse video file

**Raises**:
- `RuntimeError`: If no recording is in progress
- `ValueError`: If no frames were captured
- `OSError`: If video encoding fails or file cannot be written

**Behavior**:
- Stops frame capture
- Encodes all buffered frames into MP4 video at 5x speed
- Saves video file with timestamp-based filename
- Clears frame buffer
- Sets recording state to idle

**Side Effects**:
- Video file created on disk
- Frame buffer cleared
- Recording state set to idle
- Logs encoding completion via structured logging

**Example**:
```python
video_path = encoder.stop_recording()
print(f"Timelapse saved to: {video_path}")
# Output: timelapses/Panda-Cam-20251120-143022.mp4
```

#### `is_recording() -> bool`

Check if a recording is currently in progress.

**Returns**:
- `bool`: True if recording is active, False otherwise

**Side Effects**:
- None (read-only operation)

**Example**:
```python
if encoder.is_recording():
    print("Recording in progress...")
```

#### `get_frame_count() -> int`

Get the number of frames captured in the current recording.

**Returns**:
- `int`: Number of frames in buffer (0 if not recording)

**Raises**:
- `RuntimeError`: If no recording is in progress

**Side Effects**:
- None (read-only operation)

**Example**:
```python
frame_count = encoder.get_frame_count()
print(f"Captured {frame_count} frames")
```

#### `cancel_recording() -> None`

Cancel the current recording without saving.

**Raises**:
- `RuntimeError`: If no recording is in progress

**Behavior**:
- Stops frame capture
- Clears frame buffer
- Sets recording state to idle
- Does not create video file

**Side Effects**:
- Frame buffer cleared
- Recording state set to idle
- Logs cancellation via structured logging

**Example**:
```python
encoder.cancel_recording()
# Recording cancelled, no file saved
```

## Exceptions

### `TimelapseEncoderError`

Base exception for timelapse encoder errors.

**Attributes**:
- `message` (str): Human-readable error message
- `error_type` (str): Error category (e.g., "encoding", "disk_space", "invalid_frame")

### `RecordingInProgressError`

Raised when attempting to start a recording while one is already active.

**Inherits from**: `TimelapseEncoderError`

### `NoRecordingError`

Raised when attempting to perform recording operations when no recording is active.

**Inherits from**: `TimelapseEncoderError`

### `EncodingError`

Raised when video encoding fails.

**Inherits from**: `TimelapseEncoderError`

**Error Types**:
- `"disk_full"`: Insufficient disk space
- `"codec_error"`: Video codec encoding failed
- `"invalid_frames"`: Frame data invalid for encoding

### `DiskSpaceError`

Raised when insufficient disk space is detected.

**Inherits from**: `TimelapseEncoderError`

## Usage Example

```python
from pick_a_zoo.core.timelapse_encoder import TimelapseEncoder
from pick_a_zoo.core.video_player import VideoPlayer
import numpy as np

# Initialize encoder
encoder = TimelapseEncoder()

# Start recording
encoder.start_recording("Panda Cam", source_fps=30.0)

# Capture frames from video player
player = VideoPlayer("https://example.org/stream.m3u8")
player.load()
player.play()

while encoder.is_recording():
    frame = player.get_frame()
    if frame:
        # Convert frame to numpy array
        frame_array = frame.pixels  # Assuming VideoFrame has pixels attribute
        encoder.capture_frame(frame_array)

# Stop recording and save
video_path = encoder.stop_recording()
print(f"Timelapse saved: {video_path}")
```

## Implementation Notes

- Frame buffer stored in memory as list of numpy arrays
- Encoding uses imageio-ffmpeg with MP4/H.264 codec
- Output fps = source_fps * 5 for 5x speed effect
- Filename format: `<feed-name>-YYYYMMDD-HHMMSS.mp4`
- Directory created automatically if missing
- Disk space checked before starting recording
- Partial recordings saved on error (if at least 1 frame captured)

## Dependencies

- `imageio-ffmpeg`: Video encoding (MP4/H.264)
- `numpy`: Frame data manipulation
- `platformdirs`: Cross-platform directory paths
- `loguru`: Structured logging

## Testing

Unit tests should cover:
- Recording start/stop lifecycle
- Frame capture and buffering
- Video encoding at correct speed
- Error handling (disk space, encoding errors)
- Filename generation and uniqueness
- Directory creation and management
