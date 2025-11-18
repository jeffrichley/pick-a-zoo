# Video Window GUI Contract

**Module**: `pick_a_zoo.gui.video_window`
**Type**: GUI Component (PyQt6)
**Constitution**: Library-First Architecture (Principle II) - Uses video_player library

## Overview

The Video Window is a PyQt6 GUI component that displays a video stream in a resizable window. It uses the video_player library for playback logic and handles window management, user interaction, and error display. All video windows run in the same process as the TUI, managed by a single QApplication instance running in a separate thread.

## Interface

### `VideoWindow`

PyQt6 QMainWindow subclass for video display.

#### `__init__(feed_name: str, stream_url: str, width: int = 1280, height: int = 720) -> None`

Initialize video window with feed information and dimensions.

**Parameters**:
- `feed_name` (str): Name of the feed being displayed (for window title)
- `stream_url` (str): URL of the video stream to play
- `width` (int): Initial window width in pixels (default: 1280)
- `height` (int): Initial window height in pixels (default: 720)

**Behavior**:
- Creates QMainWindow with video display area
- Sets window title to feed name
- Sets minimum size to 320x240, maximum to 7680x4320
- Initializes video player library
- Sets up resize event handlers

**Side Effects**:
- Window created but not shown (call `show()` to display)
- Logs window creation via structured logging

**Example**:
```python
from pick_a_zoo.gui.video_window import VideoWindow

window = VideoWindow(
    feed_name="Panda Cam",
    stream_url="https://example.org/panda.m3u8",
    width=1280,
    height=720
)
window.show()
```

#### `show() -> None`

Display the video window and start playback.

**Returns**: None

**Behavior**:
- Shows the window
- Starts loading stream automatically (FR-002)
- Begins playback when stream loaded
- Displays error if stream fails to load

**Side Effects**:
- Window becomes visible
- Stream loading initiated
- Logs show event via structured logging

**Example**:
```python
window.show()  # Window appears and stream starts loading
```

#### `closeEvent(event: QCloseEvent) -> None`

Handle window close event.

**Parameters**:
- `event` (QCloseEvent): Qt close event

**Behavior**:
- Saves current window dimensions to configuration file (FR-006)
- Stops video playback
- Releases resources
- Closes window

**Side Effects**:
- Configuration file updated with new dimensions
- Video player stopped
- Window closed

**Example**:
```python
# Called automatically when user closes window
window.close()  # Triggers closeEvent
```

#### `resizeEvent(event: QResizeEvent) -> None`

Handle window resize event.

**Parameters**:
- `event` (QResizeEvent): Qt resize event

**Behavior**:
- Updates video display area to match new window size
- Tracks new dimensions for saving on close
- Debounces resize events (saves after 500ms of no resize)

**Side Effects**:
- Video display area resized
- Dimensions tracked for persistence

**Example**:
```python
# Called automatically when user resizes window
```

#### `display_error(message: str) -> None`

Display an error message in the video window.

**Parameters**:
- `message` (str): User-friendly error message to display

**Behavior**:
- Shows error message as QLabel overlay in window
- Error message is visible and clear
- Window remains closable (FR-012)

**Side Effects**:
- Error message displayed in window
- Logs error display via structured logging

**Example**:
```python
window.display_error("Stream unavailable. Please check the URL.")
```

### `launch_video_window(feed_name: str, stream_url: str, width: int = 1280, height: int = 720) -> VideoWindow`

Create and show a video window in the GUI thread.

**Parameters**:
- `feed_name` (str): Name of the feed being displayed
- `stream_url` (str): URL of the video stream to play
- `width` (int): Initial window width in pixels (default: 1280)
- `height` (int): Initial window height in pixels (default: 720)

**Returns**: `VideoWindow` object representing the created window

**Behavior**:
- Creates VideoWindow instance in the GUI thread
- Window is managed by the shared QApplication instance
- Window is added to tracked windows list
- Window is shown and stream playback begins

**Side Effects**:
- New window created in GUI thread
- Window added to tracked windows list
- Logs window creation via structured logging

**Example**:
```python
from pick_a_zoo.gui.video_window import launch_video_window

window = launch_video_window(
    feed_name="Panda Cam",
    stream_url="https://example.org/panda.m3u8",
    width=1280,
    height=720
)
# Window is tracked and will be closed when TUI exits
```

### Window Properties

#### Minimum Size

- Width: 320 pixels
- Height: 240 pixels

Enforced via `setMinimumSize(320, 240)`.

#### Maximum Size

- Width: 7680 pixels
- Height: 4320 pixels

Enforced via `setMaximumSize(7680, 4320)`.

#### Default Size

- Width: 1280 pixels
- Height: 720 pixels

Used when no saved dimensions exist.

## Error Handling

### Error Display

Errors are displayed as QLabel overlays in the video window:
- Stream unavailable: "Stream unavailable. Please check the URL."
- Network error: "Network error. Please check your connection."
- Invalid format: "Video format not supported."
- Connection lost: "Connection lost. Stream stopped."

### Error States

- **Loading**: Stream is loading, no error yet
- **Playing**: Stream playing successfully
- **Error**: Error occurred, error message displayed
- **Closed**: Window closed, window destroyed

## Threading Model

All video windows run in the same process as the TUI:
- Single QApplication instance runs in a separate thread
- QApplication manages all video windows
- TUI tracks all open windows in a list
- TUI signals GUI thread to close all windows when it exits (FR-004b)
- Multiple windows can be open simultaneously (FR-004a)
- Window objects returned from `launch_video_window()` should be stored and closed on TUI exit

## Integration with TUI

The TUI calls `launch_video_window()` when user selects a feed:
- TUI remains functional while windows are open (FR-003)
- TUI can launch multiple windows (FR-004a)
- TUI tracks all open windows and signals GUI thread to close them on exit (FR-004b)
- Window objects should be stored in TUI application and closed on exit
- GUI thread runs QApplication event loop independently of TUI event loop

## Testing

Video window GUI components can be tested:
- Unit tests with mocked video player library
- Integration tests for window lifecycle
- Thread management tests with mocked QApplication

## Dependencies

- `PyQt6`: GUI framework
- `pick_a_zoo.core.video_player`: Video playback library
- `pick_a_zoo.core.feed_manager`: Configuration file updates
- `loguru`: Structured logging
- `threading`: Thread management for GUI event loop (standard library)
