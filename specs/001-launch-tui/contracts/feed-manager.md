# Feed Manager Contract

**Module**: `pick_a_zoo.core.feed_manager`  
**Type**: Internal Library API  
**Constitution**: Library-First Architecture (Principle II)

## Overview

The Feed Manager is a standalone library module responsible for loading and saving camera feed configurations from/to YAML files. It follows the library-first architecture principle and is independently testable.

## Interface

### `load_feeds() -> list[Feed]`

Loads camera feeds from the configuration file.

**Returns**: List of Feed objects. Returns empty list if file is missing or corrupted.

**Behavior**:
- If configuration file exists and is valid: parse YAML and return list of Feed objects
- If configuration file is missing: create empty file with default structure, return empty list
- If configuration file is corrupted: rebuild empty file, log warning, return empty list
- If file is read-only: log error, return empty list (do not crash)

**Raises**:
- `PermissionError`: If file cannot be created due to permissions (propagated, not caught)
- `OSError`: If file system error occurs (propagated, not caught)

**Side Effects**:
- Creates configuration file if missing
- Rebuilds configuration file if corrupted
- Logs warnings/errors via structured logging (loguru)

**Example**:
```python
from pick_a_zoo.core.feed_manager import load_feeds

feeds = load_feeds()
# Returns: [Feed(name="Panda Cam", url="...", window_size={...}), ...]
# Or: [] if file missing/corrupted
```

### `save_feeds(feeds: list[Feed]) -> None`

Saves camera feeds to the configuration file atomically.

**Parameters**:
- `feeds` (list[Feed]): List of Feed objects to save

**Behavior**:
- Validates all Feed objects before saving
- Writes to temporary file first
- Atomically renames temporary file to final location (prevents corruption)
- Creates parent directory if it doesn't exist

**Raises**:
- `ValueError`: If any Feed object is invalid
- `PermissionError`: If file cannot be written due to permissions
- `OSError`: If file system error occurs

**Side Effects**:
- Updates configuration file on disk
- Logs save operation via structured logging

**Example**:
```python
from pick_a_zoo.core.feed_manager import save_feeds, Feed

feeds = [
    Feed(name="Panda Cam", url="https://example.org/panda.m3u8"),
    Feed(name="Otter Live", url="https://example.org/otter.mp4"),
]
save_feeds(feeds)
```

### `get_config_path() -> Path`

Returns the path to the configuration file.

**Returns**: `pathlib.Path` object pointing to feeds.yaml in platform-appropriate user data directory

**Behavior**:
- Uses `platformdirs` to determine correct location per OS
- Returns path even if file doesn't exist yet

**Example**:
```python
from pick_a_zoo.core.feed_manager import get_config_path

config_path = get_config_path()
# Returns: Path("/home/user/.local/share/pick-a-zoo/feeds.yaml") on Linux
# Or: Path("C:/Users/User/AppData/Local/pick-a-zoo/feeds.yaml") on Windows
```

## Data Types

### `Feed`

Pydantic model representing a camera feed entry.

**Fields**:
- `name: str` - Feed name (required, non-empty)
- `url: str` - Feed URL (required, valid URL format)
- `window_size: WindowSize | None` - Optional window dimensions

**Validation**:
- Name must be non-empty string
- URL must be valid URL format
- WindowSize must have positive width and height if present

### `WindowSize`

Pydantic model for window dimensions.

**Fields**:
- `width: int` - Window width in pixels (required, > 0)
- `height: int` - Window height in pixels (required, > 0)

## Error Handling

All functions use structured logging (loguru) for errors and warnings. Functions do not catch all exceptions - they propagate system-level errors (PermissionError, OSError) to allow callers to handle them appropriately.

## Testing Contract

Unit tests must cover:
- Valid YAML loading
- Missing file handling (creates empty file)
- Corrupted file handling (rebuilds empty file)
- Invalid Feed data validation
- Atomic write operations
- Cross-platform path resolution

