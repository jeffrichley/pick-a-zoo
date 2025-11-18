# Research: Launch Video Window for Selected Cam

**Feature**: 004-launch-video-window
**Date**: 2024-12-19
**Phase**: 0 - Research & Technology Decisions

## Research Questions

### 1. PyQt6 Video Window Architecture

**Question**: How should we structure PyQt6 video windows in the same process as the TUI?

**Research Findings**:
- PyQt6 requires a QApplication instance to manage windows and event loop
- Textual (TUI framework) has its own event loop that conflicts with PyQt6's event loop
- Solution: Run PyQt6 QApplication in a separate thread with its own event loop
- PyQt6 can run in threads if QApplication is created in that thread and `exec()` is called there
- Single QApplication instance can manage multiple windows
- TUI can communicate with GUI thread via signals/slots or thread-safe queues
- When TUI exits, it can signal the GUI thread to close all windows and quit the QApplication

**Decision**: Use a single QApplication instance running in a separate thread. All video windows are created and managed by this QApplication. The TUI communicates with the GUI thread to create/close windows. When the TUI exits, it signals the GUI thread to close all windows and quit the QApplication, ensuring clean shutdown.

**Rationale**: Single-process approach avoids subprocess overhead and complexity. Threading allows PyQt6 and Textual event loops to coexist. Single QApplication instance simplifies window management and ensures all windows close together when TUI exits.

**Alternatives Considered**:
- Subprocess approach: Rejected because user requirement is no subprocesses
- Single QApplication in main thread: Rejected because TUI (Textual) and GUI (PyQt6) event loops conflict
- Multiple QApplication instances: Rejected because unnecessary complexity, single instance can manage multiple windows
- Embedded Qt widgets in TUI: Rejected because Textual doesn't support embedding GUI widgets

### 2. Video Playback Library Choice

**Question**: Should we use ffpyplayer directly or wrap it in a library module?

**Research Findings**:
- ffpyplayer provides low-level video playback APIs
- Direct usage in GUI components creates tight coupling
- Library-first architecture (Constitution Principle II) requires standalone, testable modules
- ffpyplayer can be wrapped in a simple library that handles stream loading, playback control, and error handling
- Library interface should abstract away ffpyplayer specifics to allow future replacement

**Decision**: Create `core/video_player.py` library module that wraps ffpyplayer functionality. The library provides a clean interface for loading streams, starting/stopping playback, handling errors, and extracting frames. GUI components use this library rather than calling ffpyplayer directly.

**Rationale**: Follows library-first architecture principle, enables independent testing of video playback logic, and provides flexibility to swap video backends in the future if needed.

**Alternatives Considered**:
- Direct ffpyplayer usage in GUI: Rejected because it violates library-first architecture
- Use PyQt6's QMediaPlayer: Rejected because ffpyplayer provides better format support (HLS, RTSP) and is already in dependencies

### 3. Window Dimension Persistence Strategy

**Question**: How should we persist window dimensions per feed when windows run in the same process?

**Research Findings**:
- Window dimensions are stored per-feed in feeds.yaml (already established)
- Since windows run in the same process, no file locking needed for concurrent access from different processes
- Window resize events should trigger saves, but debouncing is needed to avoid excessive writes
- GUI thread can call feed_manager directly or use thread-safe communication to request saves from TUI thread

**Decision**: Use existing `feed_manager.py` library to update window dimensions. Video windows call feed_manager directly from the GUI thread to persist dimensions. Implement debouncing (save only after resize events stop for 500ms) to reduce file I/O. Since it's a single process, no file locking needed for inter-process access.

**Rationale**: Reuses existing feed_manager library, maintains consistency with other features, and debouncing prevents excessive file writes during window resizing. Single-process approach simplifies persistence without needing file locking.

**Alternatives Considered**:
- Separate window dimensions file: Rejected because it adds complexity and doesn't match existing data model
- In-memory only (no persistence): Rejected because spec requires persistence (FR-006, FR-007)
- Database instead of YAML: Rejected because it's overkill for single-user desktop app and breaks existing architecture
- Thread-safe queue for persistence requests: Rejected because direct calls are simpler in single-process architecture

### 4. Error Handling and User Feedback

**Question**: How should video windows display errors when streams fail to load or play?

**Research Findings**:
- PyQt6 provides QMessageBox for error dialogs, but this blocks the window
- Better UX: Display error message directly in the video window using QLabel
- Error states should be clearly visible and allow window closure
- Network errors, codec errors, and invalid URLs need different error messages
- Error messages should be user-friendly (not technical stack traces)

**Decision**: Video windows display error messages using QLabel widgets overlaid on the window. Error messages are user-friendly and specific (e.g., "Stream unavailable", "Network error", "Invalid video format"). Window remains closable even when displaying errors.

**Rationale**: Non-blocking error display provides better UX than modal dialogs. Overlay approach keeps error visible while allowing window management.

**Alternatives Considered**:
- Modal error dialogs: Rejected because they block interaction and are less user-friendly
- Console error logging only: Rejected because spec requires visible error messages (FR-010, FR-011)
- Separate error window: Rejected because it adds complexity and doesn't match spec requirements

### 5. Window Dimension Validation

**Question**: How should we validate window dimensions against bounds (320x240 to 7680x4320)?

**Research Findings**:
- Validation should happen when loading saved dimensions from YAML
- Validation should also happen when user resizes window (prevent resizing below minimum)
- PyQt6 QWidget has `setMinimumSize()` and `setMaximumSize()` methods
- Validation logic should be in the video_player library or feed_manager, not GUI code

**Decision**: Add validation method to `feed_manager.py` that checks dimension bounds. Video window uses `setMinimumSize(320, 240)` and `setMaximumSize(7680, 4320)` to enforce bounds during user resizing. When loading saved dimensions, feed_manager validates before returning values, using defaults if invalid.

**Rationale**: Centralizes validation logic, prevents invalid dimensions from being saved, and provides user feedback through window resize constraints.

**Alternatives Considered**:
- Validation only in GUI: Rejected because it violates library-first architecture (validation logic should be testable independently)
- No maximum size limit: Rejected because extremely large windows can cause performance issues
- Harder minimum (e.g., 640x480): Rejected because 320x240 is reasonable for small displays and matches research findings

### 6. Default Window Dimensions

**Question**: What should be the default window dimensions when no saved dimensions exist?

**Research Findings**:
- Common video player defaults: 640x480, 854x480, 1280x720
- 1280x720 (720p) is a good balance for most displays
- Should be reasonable for both small laptops and large monitors
- Default should be defined as constants in the video_player library

**Decision**: Default window dimensions: 1280x720 (width x height). Defined as constants in `core/video_player.py` for easy adjustment.

**Rationale**: 720p is a standard video resolution that works well on most displays, provides good viewing experience, and is not too large for smaller screens.

**Alternatives Considered**:
- 640x480: Rejected because it's too small for modern displays
- 1920x1080: Rejected because it's too large for many laptop screens
- Dynamic based on screen size: Rejected because it adds complexity and YAGNI principle applies

## Technology Stack Confirmation

- **PyQt6**: Confirmed for GUI windows (already in dependencies)
- **ffpyplayer**: Confirmed for video playback (already in dependencies)
- **PyYAML**: Confirmed for configuration file handling (already in dependencies)
- **threading**: Standard library for running PyQt6 QApplication in separate thread
- **loguru**: Confirmed for structured logging (already in dependencies)

## Architecture Decisions

1. **Threading Model**: Single process with PyQt6 QApplication running in a separate thread, managing all video windows
2. **Library Structure**: Video player logic in `core/video_player.py`, GUI in `gui/video_window.py`
3. **Persistence**: Use existing `feed_manager.py` for window dimension updates (direct calls from GUI thread)
4. **Error Display**: Overlay QLabel widgets in video windows for errors
5. **Validation**: Centralized in feed_manager with GUI enforcement via Qt size constraints
6. **Defaults**: 1280x720 default window size, defined in video_player library
7. **Thread Management**: TUI application manages GUI thread and signals it to close all windows and quit QApplication on exit

## Open Questions Resolved

- ✅ How to launch windows: Use single QApplication in separate thread, create windows from GUI thread
- ✅ How to structure video playback: Library module wrapping ffpyplayer
- ✅ How to persist dimensions: Use feed_manager with debouncing
- ✅ How to display errors: Overlay QLabel widgets
- ✅ How to validate dimensions: feed_manager validation + Qt size constraints
- ✅ Default dimensions: 1280x720

## Next Steps

Proceed to Phase 1: Design & Contracts
- Create data-model.md with window dimension entity details
- Create contracts for video player library interface
- Create contracts for video window GUI interface
- Create quickstart.md with implementation guidance
