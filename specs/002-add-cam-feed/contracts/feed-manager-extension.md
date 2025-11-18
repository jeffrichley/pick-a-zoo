# Feed Manager Extension Contract

**Module**: `pick_a_zoo.core.feed_manager`
**Type**: Internal Library API Extension
**Constitution**: Library-First Architecture (Principle II)

## Overview

This contract extends the existing Feed Manager contract (from Story 1) with duplicate name resolution functionality required for Story 2.

## New Interface

### `resolve_duplicate_name(name: str, existing_feeds: list[Feed]) -> str`

Resolves duplicate feed names by automatically appending a number suffix.

**Parameters**:
- `name` (str): Proposed feed name
- `existing_feeds` (list[Feed]): List of existing Feed objects to check against

**Returns**: Resolved unique name (str)

**Behavior**:
- Checks if proposed name is unique among existing feeds
- If unique: returns name as-is
- If duplicate: appends " (2)", " (3)", etc. until unique name is found
- Increments number until no conflict exists
- Handles edge cases: if "Name (2)" exists, tries "Name (3)", etc.

**Raises**:
- `ValueError`: If name is empty or invalid after processing

**Side Effects**:
- None (pure function)

**Example**:
```python
from pick_a_zoo.core.feed_manager import resolve_duplicate_name, Feed

existing = [
    Feed(name="Panda Cam", url="https://example.org/panda.m3u8"),
    Feed(name="Otter Live", url="https://example.org/otter.mp4"),
]

# Unique name
name = resolve_duplicate_name("Elephant Cam", existing)
# Returns: "Elephant Cam"

# Duplicate name
name = resolve_duplicate_name("Panda Cam", existing)
# Returns: "Panda Cam (2)"

# Multiple duplicates
existing.append(Feed(name="Panda Cam (2)", url="https://example.org/panda2.m3u8"))
name = resolve_duplicate_name("Panda Cam", existing)
# Returns: "Panda Cam (3)"
```

## Integration with Existing Functions

### `save_feeds(feeds: list[Feed]) -> None` (Extended)

**New Behavior**:
- Before saving, resolves duplicate names for all feeds in the list
- Ensures all feed names are unique before writing to file
- Maintains atomic write behavior (unchanged)

**Example**:
```python
from pick_a_zoo.core.feed_manager import save_feeds, load_feeds, Feed

existing = load_feeds()
new_feed = Feed(name="Panda Cam", url="https://example.org/new-panda.m3u8")

# If "Panda Cam" already exists, it will be automatically renamed to "Panda Cam (2)"
all_feeds = existing + [new_feed]
save_feeds(all_feeds)  # Duplicate names resolved automatically
```

## Testing Contract

Unit tests must cover:
- Unique name resolution (returns name as-is)
- Single duplicate resolution (appends " (2)")
- Multiple duplicate resolution (increments number)
- Edge cases (name with existing number suffix, empty name, etc.)
- Integration with `save_feeds()` (duplicate resolution before save)
