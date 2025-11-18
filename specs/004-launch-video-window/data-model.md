# Data Model: Launch Video Window for Selected Cam

**Feature**: Launch Video Window for Selected Cam
**Date**: 2024-12-19
**Phase**: 1 - Design & Contracts

## Entities

### Feed (Existing, Window Size Updated)

Represents a single camera feed entry loaded from the configuration file. This entity is already defined in `pick_a_zoo.core.models.Feed` and is reused for this feature. The `window_size` field will be updated when users resize video windows.

**Implementation**: Pydantic BaseModel (`pick_a_zoo.core.models.Feed`)

**Attributes**:
- `name` (string, required): Human-readable name for the feed (e.g., "Panda Cam")
- `url` (string, required): URL to the camera stream (supports m3u8, mp4, webm, rtsp, etc.)
- `window_size` (WindowSize | None, optional): Window dimensions for video playback (updated when window is resized)

**Validation Rules** (enforced by Pydantic):
- `name` must be non-empty string
- `url` must be valid URL format (validated via Pydantic's HttpUrl)
- `window_size` must be valid WindowSize model if present

**Usage in this feature**:
- Loaded via `feed_manager.load_feeds()` when launching video window
- `window_size` read when opening video window (FR-007)
- `window_size` updated when window is resized and closed (FR-006)
- Window dimensions validated against bounds (320x240 to 7680x4320) (FR-009)

### WindowSize (Existing, Validation Enhanced)

Represents window dimensions for video playback. This entity is already defined in `pick_a_zoo.core.models.WindowSize`.

**Implementation**: Pydantic BaseModel (`pick_a_zoo.core.models.WindowSize`)

**Attributes**:
- `width` (int, required): Window width in pixels
- `height` (int, required): Window height in pixels

**Validation Rules** (enforced by feed_manager and Pydantic):
- `width` must be between 320 and 7680 (inclusive)
- `height` must be between 240 and 4320 (inclusive)
- Both values must be positive integers

**New Validation Method**:
- `feed_manager.validate_window_size(width: int, height: int) -> bool`: Validates dimensions against bounds
- `feed_manager.get_validated_window_size(width: int, height: int) -> WindowSize`: Returns validated WindowSize or raises ValueError

**Usage in this feature**:
- Validated when loading saved dimensions (FR-009)
- Validated when saving resized dimensions (FR-009)
- Used to set initial window size when opening video window (FR-007)
- Updated when user resizes window (FR-006)

### VideoWindowInstance (New, Runtime Entity)

Represents a running video window. This is a runtime entity that tracks the window state but is not persisted.

**Implementation**: Runtime tracking in TUI application (required for window management)

**Attributes** (conceptual, not persisted):
- `feed_name` (string): Name of the feed being displayed
- `feed_url` (string): URL of the stream being played
- `window_object` (VideoWindow): PyQt6 VideoWindow instance
- `window_dimensions` (WindowSize): Current window dimensions (may differ from saved if user resized)

**Lifecycle**:
1. **Created**: When user selects a feed and video window is created in GUI thread
2. **Running**: Video window is active and displaying stream
3. **Closed**: User closes video window, window is destroyed and removed from tracked list
4. **Terminated**: TUI exits, all video windows are closed and GUI thread quits QApplication (FR-004b)
5. **Error**: Error occurs, error displayed in window, window remains open until user closes it

**Note**: This entity is used for window management. TUI tracks all open video windows and signals the GUI thread to close them when the TUI exits (FR-004b).

### Configuration File (feeds.yaml) (Existing, Write Access Added)

Represents the persisted state of saved cam feeds and window preferences. This entity is already defined and used by `feed_manager`. This feature adds write access for updating window dimensions.

**Structure**: Same as previous features
```yaml
feeds:
  - name: "Feed 1"
    url: "https://example.org/feed1.m3u8"
    window_size:
      width: 1280
      height: 720
  - name: "Feed 2"
    url: "https://example.org/feed2.mp4"
    window_size:
      width: 1920
      height: 1080
```

**Lifecycle in this feature**:
1. **Loading**: File loaded when opening video window to get feed URL and saved dimensions (FR-014, FR-007)
2. **Reading**: Read feed URL and window_size for selected feed (FR-014, FR-007)
3. **Writing**: Update window_size for specific feed when window is resized and closed (FR-006, FR-015)
4. **Validation**: Window dimensions validated before saving (FR-009)
5. **Error Handling**: Write errors handled gracefully without crashing (FR-016)

**New Operations**:
- `feed_manager.update_feed_window_size(feed_name: str, width: int, height: int) -> None`: Update window size for specific feed
- `feed_manager.get_feed_by_name(feed_name: str) -> Feed | None`: Get feed by name for window size updates

## Relationships

- Configuration File **contains** zero or more Feed entries (one-to-many) - existing relationship
- Feed **has** zero or one WindowSize (one-to-zero-or-one) - existing relationship, updated in this feature
- VideoWindowInstance **displays** one Feed (many-to-one) - new relationship for this feature
- Multiple VideoWindowInstance objects can exist simultaneously, each displaying a different Feed (FR-004a)

## Data Flow

1. **Window Launch**:
   - User selects feed from saved feeds list
   - `feed_manager.load_feeds()` called to get feed data
   - Feed URL extracted from selected feed (FR-014)
   - Window dimensions loaded from feed's `window_size` field (FR-007)
   - If no saved dimensions, default 1280x720 used (FR-008)
   - If saved dimensions invalid, default used (FR-009)
   - Video window created in GUI thread with feed URL and dimensions

2. **Window Resize**:
   - User resizes video window by dragging edges (FR-005)
   - Window dimensions tracked in video window instance
   - Resize events debounced (save after 500ms of no resize events)
   - New dimensions validated against bounds (FR-009)

3. **Window Close**:
   - User closes video window
   - Final window dimensions saved to configuration file (FR-006)
   - `feed_manager.update_feed_window_size()` called with feed name and dimensions
   - Configuration file updated atomically (FR-015)
   - Errors handled gracefully (FR-016)

4. **Error Handling**:
   - Stream loading errors detected in video window
   - Error messages displayed in video window (FR-010, FR-011, FR-013)
   - User can close error window and return to TUI (FR-012)
   - No configuration file updates on errors

## Validation Rules Summary

### Window Dimension Validation

**Bounds**:
- Minimum: 320x240 pixels
- Maximum: 7680x4320 pixels

**Validation Points**:
1. When loading saved dimensions from YAML (FR-009)
2. When saving resized dimensions to YAML (FR-009)
3. When user resizes window (enforced by Qt `setMinimumSize`/`setMaximumSize`)

**Default Values**:
- Default window size: 1280x720 (used when no saved dimensions exist)

**Error Handling**:
- Invalid saved dimensions → use default (FR-009)
- Write errors → log error, don't crash (FR-016)
- File locking conflicts → retry with backoff or skip save

## State Transitions

### Feed.window_size State

- `None` → `WindowSize(1280, 720)`: First time window opened, default used
- `WindowSize(w, h)` → `WindowSize(w', h')`: User resized window, new dimensions saved
- `WindowSize(invalid)` → `WindowSize(1280, 720)`: Invalid dimensions detected, default used

### VideoWindowInstance State

- **Not Started** → **Creating**: Window creation initiated in GUI thread
- **Creating** → **Running**: Window created, visible, stream loading
- **Running** → **Playing**: Stream loaded successfully, video playing
- **Running** → **Error**: Stream failed to load, error displayed
- **Playing** → **Error**: Stream connection lost during playback
- **Playing** → **Closed**: User closed window, window destroyed
- **Error** → **Closed**: User closed error window, window destroyed
- **Any State** → **Terminated**: TUI exits, all windows closed, GUI thread quits QApplication

## Data Consistency

- Window dimensions are stored per-feed in YAML (per-feed persistence)
- Multiple video windows can have different dimensions (each feed remembers its own)
- Window dimensions persist across application restarts
- Invalid dimensions are automatically corrected to defaults
- Configuration file writes are atomic to prevent corruption
