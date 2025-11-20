# Video Window Extension Contract

**Module**: `pick_a_zoo.gui.video_window`
**Type**: GUI Component Extension (PyQt6)
**Constitution**: Library-First Architecture (Principle II) - Uses timelapse_encoder library

## Overview

The Video Window extension adds timelapse recording functionality to the existing video window GUI component. It integrates a timelapse button into the video window interface and manages the recording lifecycle using the timelapse encoder library. The extension maintains separation of concerns by delegating encoding logic to the library.

## Interface Extensions

### `VideoWindow` (Extended)

PyQt6 QMainWindow subclass for video display, extended with timelapse recording capability.

#### New Attributes

- `timelapse_button` (QPushButton): PyQt6 button widget for starting/stopping timelapse recording
- `timelapse_encoder` (TimelapseEncoder | None): Encoder instance when recording is active
- `is_recording_timelapse` (bool): Whether timelapse recording is currently active

#### `__init__(feed_name: str, stream_url: str, width: int = 1280, height: int = 720) -> None`

Extended initialization to include timelapse button.

**New Behavior**:
- Creates timelapse button widget
- Adds button to window layout (toolbar or overlay)
- Sets initial button state (enabled, not recording)
- Initializes timelapse_encoder to None

**Side Effects**:
- Timelapse button created and added to window
- Button state set to "not recording"

#### `_setup_timelapse_button() -> None` (New Method)

Create and configure the timelapse button widget.

**Returns**: None

**Behavior**:
- Creates QPushButton with label "Timelapse" or icon
- Sets button style and size
- Connects button click signal to `_on_timelapse_button_clicked()`
- Adds button to window layout (toolbar area or overlay)

**Side Effects**:
- Button widget created
- Button added to window layout
- Signal-slot connection established

**Example**:
```python
def _setup_timelapse_button(self) -> None:
    from PyQt6.QtWidgets import QPushButton
    
    self.timelapse_button = QPushButton("Timelapse")
    self.timelapse_button.clicked.connect(self._on_timelapse_button_clicked)
    # Add to layout...
```

#### `_on_timelapse_button_clicked() -> None` (New Method)

Handle timelapse button click event.

**Returns**: None

**Behavior**:
- If not recording: Start recording (call `_start_timelapse_recording()`)
- If recording: Stop recording (call `_stop_timelapse_recording()`)
- Update button visual state (FR-005)

**Side Effects**:
- Recording state toggled
- Button appearance updated
- Logs button click via structured logging

**Example**:
```python
def _on_timelapse_button_clicked(self) -> None:
    if self.is_recording_timelapse:
        self._stop_timelapse_recording()
    else:
        self._start_timelapse_recording()
```

#### `_start_timelapse_recording() -> None` (New Method)

Start a new timelapse recording session.

**Returns**: None

**Raises**:
- `RuntimeError`: If recording already in progress (should not happen due to button state)
- `OSError`: If disk space insufficient (handled gracefully with error display)

**Behavior**:
- Validates that video feed is playing (FR-004)
- Creates TimelapseEncoder instance
- Calls encoder.start_recording() with feed_name and detected fps
- Sets is_recording_timelapse to True
- Updates button visual state (e.g., change text to "Stop", change color)
- Displays visual feedback (status indicator if available) (FR-005)

**Side Effects**:
- TimelapseEncoder instance created
- Recording state set to active
- Button state updated
- Visual feedback displayed
- Logs recording start via structured logging

**Example**:
```python
def _start_timelapse_recording(self) -> None:
    from pick_a_zoo.core.timelapse_encoder import TimelapseEncoder
    
    if not self._player or not self._player.is_playing():
        self.display_error("Cannot create timelapse: video not playing")
        return
    
    try:
        self.timelapse_encoder = TimelapseEncoder()
        source_fps = self._detect_source_fps() or 30.0
        self.timelapse_encoder.start_recording(self.feed_name, source_fps)
        self.is_recording_timelapse = True
        self._update_timelapse_button_state()
        self._show_status("Recording timelapse...")
    except OSError as e:
        self.display_error(f"Insufficient disk space: {e}")
    except Exception as e:
        self.display_error(f"Failed to start recording: {e}")
```

#### `_stop_timelapse_recording() -> None` (New Method)

Stop the current timelapse recording and save the video file.

**Returns**: None

**Behavior**:
- Calls encoder.stop_recording() to encode and save video
- Handles encoding errors gracefully
- Updates button visual state
- Displays success message with file path (FR-015)
- Cleans up encoder instance

**Side Effects**:
- Video file created on disk
- Recording state set to inactive
- Button state updated
- Success/error message displayed
- Encoder instance cleaned up
- Logs recording stop via structured logging

**Example**:
```python
def _stop_timelapse_recording(self) -> None:
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
```

#### `_update_timelapse_button_state() -> None` (New Method)

Update button visual appearance based on recording state.

**Returns**: None

**Behavior**:
- If recording: Change button text to "Stop Timelapse", change style (e.g., red background)
- If not recording: Change button text to "Start Timelapse", reset style
- Update button enabled/disabled state as needed

**Side Effects**:
- Button appearance updated
- Button state synchronized with recording state

**Example**:
```python
def _update_timelapse_button_state(self) -> None:
    if self.is_recording_timelapse:
        self.timelapse_button.setText("Stop Timelapse")
        self.timelapse_button.setStyleSheet("background-color: red;")
    else:
        self.timelapse_button.setText("Start Timelapse")
        self.timelapse_button.setStyleSheet("")
```

#### `_update_frame() -> None` (Extended Method)

Extended frame update to capture frames for timelapse if recording is active.

**New Behavior**:
- After displaying frame, check if recording is active
- If recording: Convert frame to numpy array and call encoder.capture_frame()
- Handle frame capture errors gracefully (log but don't stop recording)

**Side Effects**:
- Frame captured and added to recording buffer (if recording)
- Logs frame capture errors (if any)

**Example**:
```python
def _update_frame(self) -> None:
    # ... existing frame display code ...
    
    # Capture frame for timelapse if recording
    if self.is_recording_timelapse and self.timelapse_encoder:
        try:
            # Convert QPixmap/QImage to numpy array
            frame_array = self._convert_frame_to_array(scaled_pixmap)
            self.timelapse_encoder.capture_frame(frame_array)
        except Exception as e:
            logger.warning(f"Failed to capture frame: {e}")
```

#### `closeEvent(self, event: QCloseEvent | None) -> None` (Extended Method)

Extended close event handler to stop timelapse recording if active.

**New Behavior**:
- Before closing window, check if recording is active
- If recording: Stop recording and save video file
- Continue with normal window close

**Side Effects**:
- Timelapse recording stopped and saved (if active)
- Window closed normally

**Example**:
```python
def closeEvent(self, event: QCloseEvent | None) -> None:
    # Stop timelapse recording if active
    if self.is_recording_timelapse:
        self._stop_timelapse_recording()
    
    # ... existing close event code ...
```

#### `_detect_source_fps() -> float | None` (New Method, Optional)

Detect source video frame rate for accurate timelapse encoding.

**Returns**:
- `float | None`: Detected frame rate in fps, or None if cannot be determined

**Behavior**:
- Attempts to detect frame rate from VideoPlayer or stream metadata
- Returns None if detection fails (default 30.0 will be used)

**Side Effects**:
- None (read-only operation)

**Note**: This is optional - default 30.0 fps can be used if detection is not feasible.

## Visual Feedback Requirements

### Button State Changes (FR-005)

- **Not Recording**: Button shows "Start Timelapse" or icon, normal style
- **Recording**: Button shows "Stop Timelapse" or icon, highlighted/red style
- **Error**: Button disabled, error message displayed separately

### Status Indicators (FR-005)

- **Recording Active**: Display status text "Recording timelapse..." or indicator icon
- **Recording Complete**: Display success message with filename
- **Error**: Display error message in error label

## Error Handling

### Disk Space Errors (FR-014)

- Check disk space before starting recording
- Display clear error message if insufficient space
- Do not start recording if space insufficient

### Encoding Errors (FR-009)

- Display error message if encoding fails
- Attempt to save partial recording if possible (FR-011)
- Allow user to dismiss error and continue using window

### Feed Errors During Recording (FR-010)

- Stop recording automatically if feed encounters error
- Save any captured frames (partial recording)
- Display appropriate error message

## Integration Points

### With TimelapseEncoder Library

- VideoWindow creates and manages TimelapseEncoder instance
- Delegates encoding logic to library (separation of concerns)
- Handles library exceptions and displays user-friendly messages

### With VideoPlayer Library

- Captures frames from VideoPlayer.get_frame()
- Validates that player is playing before starting recording
- Handles player errors during recording

## Testing

GUI tests should cover:
- Button creation and layout
- Button click handling (start/stop)
- Visual feedback updates
- Frame capture integration
- Error handling and display
- Window close with active recording

## Dependencies

- `PyQt6`: GUI framework (existing)
- `pick_a_zoo.core.timelapse_encoder`: Timelapse encoding library (new)
- `pick_a_zoo.core.video_player`: Video playback library (existing)
- `numpy`: Frame data conversion (existing)
- `loguru`: Structured logging (existing)

