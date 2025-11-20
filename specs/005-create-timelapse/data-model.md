# Data Model: Create Timelapse Video from Active Feed

**Feature**: Create Timelapse Video from Active Feed
**Date**: 2025-11-20
**Phase**: 1 - Design & Contracts

## Entities

### TimelapseRecording (New, Runtime Entity)

Represents an active timelapse recording session. This is a runtime entity that tracks recording state but is not persisted.

**Implementation**: Runtime tracking in timelapse encoder library (`core/timelapse_encoder.py`)

**Attributes**:
- `feed_name` (string): Name of the feed being recorded (for filename)
- `start_time` (datetime): When recording started
- `frames` (list[numpy.ndarray]): Buffer of captured frames (in memory)
- `source_fps` (float): Source video frame rate (detected or default 30fps)
- `output_fps` (float): Output frame rate (source_fps * 5 for 5x speed)
- `is_recording` (bool): Whether recording is currently active
- `output_path` (Path | None): Path where video will be saved (None until recording stops)

**Lifecycle**:
1. **Created**: When user clicks timelapse button, TimelapseEncoder.start_recording() called
2. **Recording**: Frames captured from VideoPlayer and buffered
3. **Stopped**: User clicks button again or window closes, encoding begins
4. **Encoding**: Frames encoded into video file at 5x speed
5. **Completed**: Video file saved, recording object cleaned up
6. **Error**: Error occurs during recording/encoding, error handled, recording stopped

**Validation Rules**:
- `feed_name` must be non-empty string
- `source_fps` must be positive float (default 30.0 if unknown)
- `output_fps` must be exactly `source_fps * 5`
- `frames` list must not exceed memory limits (implementation-dependent threshold)

### TimelapseVideo (New, File Entity)

Represents a saved timelapse video file on disk. This entity is the output product of timelapse recording.

**Implementation**: File system entity (MP4 video file)

**Attributes** (file metadata):
- `filename` (string): Timestamp-based filename (e.g., `Panda-Cam-20251120-143022.mp4`)
- `file_path` (Path): Full path to video file in timelapses directory
- `feed_name` (string): Name of feed that was recorded (extracted from filename)
- `created_at` (datetime): When video was created (from filename timestamp)
- `duration` (float): Video duration in seconds (calculated from frame count and fps)
- `file_size` (int): Size of video file in bytes

**File Naming Convention**:
- Format: `<feed-name>-YYYYMMDD-HHMMSS.mp4`
- Feed name sanitized (spaces → hyphens, special chars removed)
- Timestamp ensures uniqueness
- Extension: `.mp4` (H.264 codec)

**Storage Location**:
- Base directory: `platformdirs.user_data_dir('pick-a-zoo') / 'timelapses'`
- Directory created automatically if missing
- Cross-platform path handling via platformdirs

**Validation Rules**:
- Filename must match pattern: `^[A-Za-z0-9-]+-\d{8}-\d{6}\.mp4$`
- File must exist at file_path
- File must be valid MP4 format (playable by standard players)
- File size must be > 0 bytes

### VideoWindowInstance (Existing, Extended)

Represents a running video window. Extended with timelapse recording state tracking.

**Implementation**: Runtime tracking in video window (`gui/video_window.py`)

**New Attributes** (for this feature):
- `timelapse_encoder` (TimelapseEncoder | None): Encoder instance if recording active
- `is_recording_timelapse` (bool): Whether timelapse recording is currently active
- `timelapse_button` (QPushButton): PyQt6 button widget for timelapse control

**Extended Lifecycle**:
- **Recording Started**: User clicks timelapse button, encoder created, button state updated
- **Recording Active**: Frames captured during normal playback, visual feedback shown
- **Recording Stopped**: User clicks button again or window closes, encoding triggered
- **Recording Error**: Error during recording, recording stopped, error displayed

### TimelapseEncoder (New, Library Class)

Represents the timelapse encoding library component. This is the core library class that handles frame capture and video encoding.

**Implementation**: Library class (`core/timelapse_encoder.py`)

**State**:
- **Idle**: No active recording
- **Recording**: Actively capturing frames
- **Encoding**: Processing captured frames into video file
- **Error**: Error state, recording stopped

**Methods** (see contracts for full API):
- `start_recording(feed_name: str, source_fps: float = 30.0) -> None`
- `capture_frame(frame: numpy.ndarray) -> None`
- `stop_recording() -> Path`
- `is_recording() -> bool`

## Relationships

- VideoWindowInstance **has** zero or one TimelapseEncoder (one-to-zero-or-one) - new relationship
- TimelapseEncoder **creates** one TimelapseVideo (one-to-one) - new relationship
- VideoWindowInstance **displays** one Feed (many-to-one) - existing relationship
- TimelapseVideo **records** one Feed (many-to-one) - new relationship (via feed_name)

## Data Flow

1. **Recording Start**:
   - User clicks timelapse button in video window
   - VideoWindow creates TimelapseEncoder instance
   - TimelapseEncoder.start_recording() called with feed_name
   - Recording state set to active
   - Button visual feedback updated (FR-005)
   - Frame capture begins

2. **Frame Capture**:
   - VideoWindow._update_frame() captures frames from VideoPlayer
   - If recording active, frame passed to TimelapseEncoder.capture_frame()
   - Frame added to in-memory buffer
   - Frame capture continues until recording stopped

3. **Recording Stop**:
   - User clicks timelapse button again OR window closes
   - TimelapseEncoder.stop_recording() called
   - Frames encoded into MP4 video at 5x speed (FR-003)
   - Video file saved to timelapses directory (FR-007)
   - Filename generated with timestamp (FR-004)
   - Recording state reset to idle
   - Button visual feedback updated

4. **Error Handling**:
   - Disk space error: Check before starting, display error, don't start (FR-014)
   - Encoding error: Display error, attempt to save partial recording (FR-011)
   - Feed error: Stop recording, save captured frames (FR-010)
   - Memory error: Flush buffer early, encode partial video

## Validation Rules Summary

### Recording State Validation

**Pre-conditions for Starting Recording**:
- Video feed must be playing (FR-004)
- No other recording must be active (FR-012)
- Sufficient disk space available (FR-014)
- Feed name must be valid (non-empty string)

**Frame Capture Validation**:
- Frame must be valid numpy array with shape (height, width, 3) for RGB
- Frame dimensions must match source video dimensions (or handle resolution changes)
- Frame buffer must not exceed memory limits

**Encoding Validation**:
- Must have at least 1 frame captured
- Output fps must be exactly 5x source fps
- Output directory must be writable
- Filename must be unique (timestamp ensures this)

### File Naming Validation

**Filename Format**:
- Pattern: `<sanitized-feed-name>-YYYYMMDD-HHMMSS.mp4`
- Feed name sanitization: spaces → hyphens, remove special chars except hyphens
- Timestamp: 8 digits date + 6 digits time (24-hour format)
- Extension: `.mp4`

**Uniqueness**:
- Timestamp-based naming ensures uniqueness (FR-004)
- If collision occurs (unlikely), append sequence number: `-YYYYMMDD-HHMMSS-2.mp4`

### Directory Validation

**Timelapses Directory**:
- Created automatically if missing (FR-007)
- Located in application data directory via platformdirs
- Must be writable by application
- Error handling if directory cannot be created

## State Transitions

### TimelapseEncoder State

- **Idle** → **Recording**: User clicks button, start_recording() called
- **Recording** → **Encoding**: User clicks button again or window closes, stop_recording() called
- **Encoding** → **Idle**: Video file saved successfully
- **Recording** → **Error**: Error during capture (feed error, memory error)
- **Encoding** → **Error**: Error during encoding (disk full, codec error)
- **Error** → **Idle**: Error handled, recording cleaned up

### VideoWindow Timelapse Button State

- **Enabled** (not recording) → **Active** (recording): Button clicked, recording started
- **Active** (recording) → **Enabled** (not recording): Button clicked again, recording stopped
- **Active** → **Disabled**: Error occurred, recording stopped automatically
- **Any** → **Disabled**: Window closing, recording stopped

## Data Consistency

- Only one recording can be active per video window (FR-012)
- Recording state synchronized between VideoWindow and TimelapseEncoder
- Frame buffer cleared after encoding completes
- Video files are atomic (saved only after successful encoding)
- Partial recordings saved on error (FR-011)
- Timestamp-based filenames prevent conflicts (FR-004)

## Performance Considerations

- Frame buffer size limited to prevent memory exhaustion
- Encoding happens asynchronously or in background thread to avoid blocking playback
- Disk space checked before starting recording (FR-014)
- Frame capture rate matches video playback rate (no additional overhead)
- Encoding performance optimized for reasonable recording durations (minutes, not hours)
