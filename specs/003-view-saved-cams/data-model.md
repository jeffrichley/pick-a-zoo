# Data Model: View Saved Cam Feeds in TUI

**Feature**: View Saved Cam Feeds in TUI
**Date**: 2024-12-19
**Phase**: 1 - Design & Contracts

## Entities

### Feed (Existing)

Represents a single camera feed entry loaded from the configuration file. This entity is already defined in `pick_a_zoo.core.models.Feed` and is reused for this feature.

**Implementation**: Pydantic BaseModel (`pick_a_zoo.core.models.Feed`)

**Attributes**:
- `name` (string, required): Human-readable name for the feed (e.g., "Panda Cam")
- `url` (string, required): URL to the camera stream (supports m3u8, mp4, webm, rtsp, etc.)
- `window_size` (WindowSize | None, optional): Window dimensions for video playback

**Validation Rules** (enforced by Pydantic):
- `name` must be non-empty string
- `url` must be valid URL format (validated via Pydantic's HttpUrl)
- `window_size` must be valid WindowSize model if present

**Usage in this feature**:
- Loaded via `feed_manager.load_feeds()`
- Filtered to remove entries with invalid or missing URLs (FR-013a)
- Sorted alphabetically by name for display (FR-005)
- Displayed with visual distinction for duplicates (FR-021)
- Truncated if name exceeds terminal width (FR-022)

### Display Feed (Derived)

Represents a feed entry as displayed in the TUI list, with display-specific transformations applied.

**Derived From**: `Feed` entity

**Display Transformations**:
- **Duplicate Name Resolution**: If duplicate names exist, display names are modified to include number suffix (e.g., "Panda Cam (2)") (FR-021)
- **Name Truncation**: Long names are truncated with ellipsis to fit terminal width (FR-022)
- **Emoji Icon**: Each feed is displayed with a small emoji icon (FR-004)

**Note**: Display transformations are applied at render time, not persisted to the configuration file (FR-019).

### Configuration File (feeds.yaml) (Existing)

Represents the persisted collection of all saved cam feeds. This entity is already defined and used by `feed_manager`.

**Structure**: Same as Story 1 and Story 2
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

**Lifecycle in this feature**:
1. **Loading**: File loaded once when screen is entered (FR-023)
2. **Reading**: Read-only access (FR-019) - no writes performed
3. **Validation**: Invalid entries are skipped during loading (FR-013, FR-013a)
4. **Recovery**: Corrupted files are handled gracefully (FR-012, FR-014)

## Relationships

- Configuration File **contains** zero or more Feed entries (one-to-many) - existing relationship
- ViewSavedCamsScreen **displays** zero or more Feed entries (one-to-many) - new relationship for this feature

## Data Flow

1. **Screen Entry**:
   - User selects "View Saved Cams" from main menu
   - `ViewSavedCamsScreen.on_mount()` called
   - Call `feed_manager.load_feeds()` to load all feeds from YAML
   - Filter feeds: skip entries with invalid or missing URLs (FR-013a)
   - Sort feeds alphabetically by name (FR-005)
   - Resolve duplicate names for display (FR-021)
   - Cache feeds list in memory for session duration (FR-023)

2. **List Display**:
   - Convert each Feed to ListItem widget
   - Apply name truncation based on terminal width (FR-022)
   - Add emoji icon to each feed entry (FR-004)
   - Display in scrollable ListView (FR-003)

3. **User Navigation**:
   - User navigates with arrow keys or WASD (FR-006)
   - ListView handles scrolling to keep selected item visible (FR-016)
   - Highlight currently selected feed (FR-007)

4. **Feed Selection**:
   - User confirms selection with Enter key (FR-008)
   - Transition to watch action with selected Feed (FR-009)
   - Feed object passed to watch screen (future Story 4)

5. **Screen Exit**:
   - User returns to main menu
   - Screen unmounted, cached feeds list discarded
   - On re-entry, feeds are reloaded from file (FR-023)

## Constraints

### Display Constraints

- **Name Length**: Feed names are truncated to fit terminal width with ellipsis (FR-022)
- **Duplicate Names**: All duplicates displayed with visual distinction (FR-021)
- **Invalid Entries**: Feeds with invalid or missing URLs are not displayed (FR-013a)
- **Empty State**: If no valid feeds, display "No feeds saved" message (FR-010)

### Performance Constraints

- **Load Time**: Feeds list must display within 1 second (SC-001)
- **List Size**: No explicit limit, but must handle unlimited feeds with scrolling (FR-003, FR-016)

### Data Integrity Constraints

- **Read-Only**: No modifications to configuration file during viewing (FR-019)
- **Session Isolation**: File modifications by other processes don't affect active viewing (FR-023)
- **Validation**: Invalid entries are skipped, not displayed (FR-013, FR-013a)

## State Transitions

### Feed Loading States

- **Not Loaded** → **Loading** (on screen mount)
- **Loading** → **Loaded** (feeds loaded successfully)
- **Loading** → **Empty** (no feeds or all invalid)
- **Loading** → **Error** (file read error, display error message)

### List Display States

- **Empty** → **Populated** (feeds loaded and displayed)
- **Populated** → **Selected** (user navigates to feed)
- **Selected** → **Watching** (user confirms selection, transitions to watch action)

### Screen States

- **Hidden** → **Visible** (screen pushed)
- **Visible** → **Hidden** (screen popped, returns to main menu)
- **Visible** → **Resized** (terminal resize, layout adjusts automatically)

## Validation Rules

### Feed Validation (Applied During Loading)

1. **URL Validation**: Feed must have valid, non-empty URL (FR-013a)
   - Invalid URLs: empty string, None, malformed URL
   - Validated via Pydantic's HttpUrl type

2. **Name Validation**: Feed must have valid, non-empty name (existing Feed model validation)
   - Invalid names: empty string, None
   - Validated via Pydantic model

3. **Structure Validation**: Feed must match Feed model structure (existing validation)
   - Invalid entries: missing required fields, wrong types
   - Validated via Pydantic model parsing

### Display Validation (Applied During Rendering)

1. **Duplicate Name Resolution**: Ensure unique display names (FR-021)
   - Check all feed names for duplicates
   - Append number suffix to duplicates (e.g., " (2)", " (3)")

2. **Name Truncation**: Ensure names fit terminal width (FR-022)
   - Calculate available width (terminal width - emoji width - padding)
   - Truncate with ellipsis if exceeds width

## Data Transformations

### Feed → Display Feed

```python
def prepare_feed_for_display(feed: Feed, all_feeds: list[Feed], terminal_width: int) -> DisplayFeed:
    # Resolve duplicate name
    display_name = resolve_duplicate_name(feed, all_feeds)

    # Truncate if needed
    max_name_width = terminal_width - 4  # Account for emoji and padding
    display_name = truncate_name(display_name, max_name_width)

    return DisplayFeed(
        feed=feed,
        display_name=display_name,
        emoji_icon="📹"  # Or feed-specific emoji
    )
```

### Feed List → Sorted List

```python
def prepare_feeds_list(feeds: list[Feed]) -> list[Feed]:
    # Filter invalid entries
    valid_feeds = [f for f in feeds if f.url and is_valid_url(f.url)]

    # Sort alphabetically
    sorted_feeds = sorted(valid_feeds, key=lambda f: f.name.lower())

    return sorted_feeds
```
