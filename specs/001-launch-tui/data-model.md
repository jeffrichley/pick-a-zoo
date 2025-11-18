# Data Model: Launch the Pick-a-Zoo TUI

**Feature**: Launch the Pick-a-Zoo TUI
**Date**: 2024-12-19
**Phase**: 1 - Design & Contracts

## Entities

### Feed

Represents a single camera feed entry stored in the configuration file. Implemented as a Pydantic model for automatic validation and type safety.

**Implementation**: Pydantic BaseModel (`pick_a_zoo.core.models.Feed`)

**Attributes**:
- `name` (string, required): Human-readable name for the feed (e.g., "Panda Cam")
- `url` (string, required): URL to the camera stream (supports m3u8, mp4, webm, rtsp, etc.)
- `window_size` (WindowSize | None, optional): Window dimensions for video playback

**Validation Rules** (enforced by Pydantic):
- `name` must be non-empty string
- `url` must be valid URL format (validated via Pydantic's HttpUrl or custom validator)
- `window_size` must be valid WindowSize model if present

### WindowSize

Represents window dimensions for video playback. Implemented as a Pydantic model.

**Implementation**: Pydantic BaseModel (`pick_a_zoo.core.models.WindowSize`)

**Attributes**:
- `width` (integer, required): Window width in pixels (must be > 0)
- `height` (integer, required): Window height in pixels (must be > 0)

**Validation Rules** (enforced by Pydantic):
- `width` and `height` must be positive integers

**Example**:
```yaml
name: "Panda Cam"
url: "https://example.org/panda.m3u8"
window_size:
  width: 1280
  height: 720
```

### Configuration File (feeds.yaml)

Represents the persisted state of all saved camera feeds.

**Structure**:
```yaml
feeds:
  - name: "Feed 1"
    url: "https://example.org/feed1.m3u8"
    window_size:
      width: 1280
      height: 720
  - name: "Feed 2"
    url: "https://example.org/feed2.mp4"
```

**File Location**: Determined by `platformdirs` library (cross-platform user data directory)

**Lifecycle**:
1. **Creation**: File created automatically if missing on first access
2. **Loading**: File loaded on application startup
3. **Saving**: File saved atomically when feeds are modified
4. **Recovery**: If corrupted, system rebuilds empty file and displays warning

**State Transitions**:
- **Missing** → **Empty** (auto-created with empty feeds list)
- **Valid** → **Valid** (normal updates)
- **Corrupted** → **Empty** (recovery: rebuild safe empty file)

## Relationships

- Configuration File **contains** zero or more Feed entries (one-to-many)

## Data Flow

1. **Application Startup**:
   - Load feeds.yaml via `feed_manager.load_feeds()`
   - If missing: create empty file, return empty list
   - If corrupted: rebuild empty file, return empty list, display warning
   - Display feed count in TUI menu

2. **Feed Addition** (future story):
   - User adds new feed via TUI
   - Call `feed_manager.save_feeds()` with updated list
   - Atomic write to feeds.yaml

3. **Feed Selection** (future story):
   - User selects feed from menu
   - Load feed URL and window_size
   - Launch video player with feed details

## Constraints

- Configuration file must always be valid YAML (even if empty)
- File writes must be atomic to prevent corruption
- Feed names should be unique (enforced in future story, not required for Story 1)
- Maximum file size: No explicit limit, but practical limit based on reasonable number of feeds (< 1000)
