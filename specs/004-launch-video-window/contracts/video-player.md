# Video Player Library Contract

**Module**: `pick_a_zoo.core.video_player`
**Type**: Internal Library API
**Constitution**: Library-First Architecture (Principle II)

## Overview

The Video Player library is a standalone, independently testable module that provides video playback functionality. It wraps ffpyplayer to provide a clean interface for loading streams, controlling playback, handling errors, and extracting frames. The library is GUI-agnostic and can be used by any video display component.

## Interface

### `VideoPlayer`

Main class for video playback operations.

#### `__init__(stream_url: str) -> None`

Initialize video player with a stream URL.

**Parameters**:
- `stream_url` (str): URL of the video stream to play (supports m3u8, mp4, webm, rtsp, etc.)

**Raises**:
- `ValueError`: If stream_url is empty or invalid format
- `VideoPlayerError`: If initialization fails

**Side Effects**:
- None (lazy initialization, stream not loaded until `load()` called)

**Example**:
```python
from pick_a_zoo.core.video_player import VideoPlayer

player = VideoPlayer("https://example.org/stream.m3u8")
```

#### `load() -> None`

Load the video stream and prepare for playback.

**Returns**: None

**Behavior**:
- Attempts to connect to stream URL
- Validates stream format and accessibility
- Prepares video decoder and buffers
- Raises error if stream cannot be loaded

**Raises**:
- `StreamLoadError`: If stream URL is inaccessible, invalid format, or network error
- `VideoPlayerError`: If video player initialization fails

**Side Effects**:
- Network I/O (stream connection)
- Logs loading process via structured logging

**Example**:
```python
try:
    player.load()
except StreamLoadError as e:
    print(f"Failed to load stream: {e}")
```

#### `play() -> None`

Start video playback.

**Returns**: None

**Behavior**:
- Begins decoding and displaying video frames
- Playback starts automatically after load
- If already playing, has no effect

**Raises**:
- `VideoPlayerError`: If playback cannot start (stream not loaded, codec error, etc.)

**Side Effects**:
- Video frames decoded and available for display
- Logs playback events via structured logging

**Example**:
```python
player.load()
player.play()
```

#### `stop() -> None`

Stop video playback and release resources.

**Returns**: None

**Behavior**:
- Stops decoding and frame generation
- Releases video decoder and buffers
- Cleans up network connections

**Side Effects**:
- Resources released
- Logs stop event via structured logging

**Example**:
```python
player.stop()
```

#### `get_frame() -> VideoFrame | None`

Get the next video frame for display.

**Returns**: `VideoFrame` object with frame data, or `None` if no frame available

**Behavior**:
- Returns decoded video frame if available
- Returns `None` if playback stopped or no frame ready
- Frame contains pixel data and timestamp

**Side Effects**:
- None (read-only operation)

**Example**:
```python
frame = player.get_frame()
if frame:
    # Display frame in GUI
    display_frame(frame.pixels, frame.width, frame.height)
```

#### `is_playing() -> bool`

Check if video is currently playing.

**Returns**: `True` if playing, `False` otherwise

**Example**:
```python
if player.is_playing():
    frame = player.get_frame()
```

#### `get_error() -> VideoPlayerError | None`

Get the last error that occurred, if any.

**Returns**: `VideoPlayerError` object if error occurred, `None` otherwise

**Behavior**:
- Returns most recent error
- Error cleared when new operation succeeds

**Example**:
```python
error = player.get_error()
if error:
    print(f"Error: {error.message}")
```

### Exceptions

#### `VideoPlayerError`

Base exception for video player errors.

**Attributes**:
- `message` (str): Human-readable error message
- `error_type` (str): Error category (e.g., "network", "codec", "stream")

#### `StreamLoadError(VideoPlayerError)`

Raised when stream cannot be loaded.

**Error Types**:
- `"network"`: Network connectivity issue
- `"unavailable"`: Stream URL returns 404 or similar
- `"timeout"`: Connection timeout
- `"invalid_format"`: Stream format not supported

### Constants

#### `DEFAULT_WINDOW_WIDTH = 1280`

Default window width in pixels.

#### `DEFAULT_WINDOW_HEIGHT = 720`

Default window height in pixels.

#### `MIN_WINDOW_WIDTH = 320`

Minimum valid window width in pixels.

#### `MIN_WINDOW_HEIGHT = 240`

Minimum valid window height in pixels.

#### `MAX_WINDOW_WIDTH = 7680`

Maximum valid window width in pixels.

#### `MAX_WINDOW_HEIGHT = 4320`

Maximum valid window height in pixels.

## Usage Pattern

```python
from pick_a_zoo.core.video_player import VideoPlayer, StreamLoadError

# Create player
player = VideoPlayer("https://example.org/stream.m3u8")

try:
    # Load stream
    player.load()

    # Start playback
    player.play()

    # Display frames (in GUI event loop)
    while player.is_playing():
        frame = player.get_frame()
        if frame:
            display_frame(frame)

except StreamLoadError as e:
    # Handle load error
    show_error(f"Failed to load stream: {e.message}")
finally:
    # Clean up
    player.stop()
```

## Testing

The video player library is independently testable:
- Mock ffpyplayer for unit tests
- Test stream loading with test URLs
- Test error handling with invalid URLs
- Test frame extraction without GUI dependencies

## Dependencies

- `ffpyplayer`: Video playback engine
- `loguru`: Structured logging
- Standard library: No external dependencies beyond ffpyplayer
