# Feed Manager Extension Contract

**Module**: `pick_a_zoo.core.feed_manager`
**Type**: Internal Library API Extension
**Constitution**: Library-First Architecture (Principle II)

## Overview

Extensions to the existing `feed_manager` library to support window dimension persistence. These methods add write access for updating window dimensions per feed while maintaining the library's independent, testable design.

## New Methods

### `update_feed_window_size(feed_name: str, width: int, height: int) -> None`

Update the window size for a specific feed in the configuration file.

**Parameters**:
- `feed_name` (str): Name of the feed to update
- `width` (int): New window width in pixels (must be 320-7680)
- `height` (int): New window height in pixels (must be 240-4320)

**Returns**: None

**Behavior**:
- Loads current feeds from configuration file
- Finds feed with matching name
- Validates width and height against bounds (320x240 to 7680x4320)
- Updates feed's `window_size` field
- Saves updated feeds to configuration file atomically
- If feed not found, raises `FeedNotFoundError`
- If dimensions invalid, raises `ValueError`

**Raises**:
- `FeedNotFoundError`: If feed with given name doesn't exist
- `ValueError`: If width or height outside valid bounds
- `ConfigurationError`: If configuration file cannot be read or written

**Side Effects**:
- Configuration file updated
- Logs update operation via structured logging

**Example**:
```python
from pick_a_zoo.core.feed_manager import update_feed_window_size

try:
    update_feed_window_size("Panda Cam", 1920, 1080)
except FeedNotFoundError:
    print("Feed not found")
except ValueError as e:
    print(f"Invalid dimensions: {e}")
```

### `get_feed_by_name(feed_name: str) -> Feed | None`

Get a feed by name from the configuration file.

**Parameters**:
- `feed_name` (str): Name of the feed to retrieve

**Returns**: `Feed` object if found, `None` if not found

**Behavior**:
- Loads feeds from configuration file
- Searches for feed with matching name (case-sensitive)
- Returns Feed object if found
- Returns `None` if not found

**Raises**:
- `ConfigurationError`: If configuration file cannot be read

**Side Effects**:
- None (read-only operation)
- Logs retrieval operation via structured logging

**Example**:
```python
from pick_a_zoo.core.feed_manager import get_feed_by_name

feed = get_feed_by_name("Panda Cam")
if feed:
    print(f"Found feed: {feed.url}")
    if feed.window_size:
        print(f"Window size: {feed.window_size.width}x{feed.window_size.height}")
```

### `validate_window_size(width: int, height: int) -> bool`

Validate window dimensions against bounds.

**Parameters**:
- `width` (int): Window width in pixels
- `height` (int): Window height in pixels

**Returns**: `True` if dimensions are valid, `False` otherwise

**Behavior**:
- Checks width is between 320 and 7680 (inclusive)
- Checks height is between 240 and 4320 (inclusive)
- Returns `True` if both valid, `False` otherwise

**Side Effects**:
- None (pure validation function)

**Example**:
```python
from pick_a_zoo.core.feed_manager import validate_window_size

if validate_window_size(1280, 720):
    print("Valid dimensions")
else:
    print("Invalid dimensions")
```

### `get_validated_window_size(width: int, height: int) -> WindowSize`

Get a validated WindowSize object or raise error.

**Parameters**:
- `width` (int): Window width in pixels
- `height` (int): Window height in pixels

**Returns**: `WindowSize` object with validated dimensions

**Behavior**:
- Validates dimensions against bounds
- Returns `WindowSize` object if valid
- Raises `ValueError` if invalid

**Raises**:
- `ValueError`: If width or height outside valid bounds

**Side Effects**:
- None (pure validation function)

**Example**:
```python
from pick_a_zoo.core.feed_manager import get_validated_window_size

try:
    window_size = get_validated_window_size(1280, 720)
except ValueError as e:
    print(f"Invalid dimensions: {e}")
```

## New Exceptions

### `FeedNotFoundError(Exception)`

Raised when a feed with the specified name is not found.

**Attributes**:
- `feed_name` (str): Name of the feed that was not found
- `message` (str): Human-readable error message

## Usage Pattern

```python
from pick_a_zoo.core.feed_manager import (
    get_feed_by_name,
    update_feed_window_size,
    validate_window_size
)

# Get feed to launch window
feed = get_feed_by_name("Panda Cam")
if feed:
    # Launch window with saved dimensions or defaults
    width = feed.window_size.width if feed.window_size else 1280
    height = feed.window_size.height if feed.window_size else 720

    # Launch video window...

    # When window closes, save new dimensions
    if validate_window_size(new_width, new_height):
        update_feed_window_size("Panda Cam", new_width, new_height)
```

## Integration with Video Window

Video windows call `update_feed_window_size()` when closed:
- Window tracks dimensions during resize
- On close, calls `update_feed_window_size()` with final dimensions
- Uses debouncing to avoid excessive file writes during resize

## Testing

New methods are independently testable:
- Test `update_feed_window_size()` with valid/invalid dimensions
- Test `get_feed_by_name()` with existing/non-existing feeds
- Test `validate_window_size()` with various dimension values
- Test error handling for file I/O errors

## Backward Compatibility

All new methods are additive - existing `feed_manager` functionality remains unchanged:
- `load_feeds()` still works as before
- `save_feeds()` still works as before
- New methods extend functionality without breaking changes
