# View Saved Cams Screen Contract

**Module**: `pick_a_zoo.tui.screens.view_saved_cams`
**Type**: TUI Screen Component
**Constitution**: Library-First Architecture (Principle II)

## Overview

The View Saved Cams Screen is a Textual screen component that displays all saved camera feeds in a scrollable, selectable list. Users can navigate through feeds using arrow keys or WASD keys, view feeds sorted alphabetically, and select a feed to transition to the watch action.

## Interface

### `ViewSavedCamsScreen`

Textual Screen class for displaying saved camera feeds list.

**Inherits**: `textual.screen.Screen`

**Key Bindings**:
- `up`, `w`: Navigate up in list
- `down`, `s`: Navigate down in list
- `left`, `a`: Navigate left (no-op in list)
- `right`, `d`: Navigate right (no-op in list)
- `enter`: Select feed and transition to watch action
- `escape`, `q`: Return to main menu

**Methods**:

#### `compose() -> ComposeResult`

Composes the screen layout with ListView widget.

**Returns**: ComposeResult containing screen widgets

**Widgets**:
- `ListView` (id="feeds-list"): Scrollable list of feeds
- `Static` (id="empty-message"): Empty state message (hidden when feeds exist)
- `Static` (id="error-message"): Error message (hidden when no errors)

**Example**:
```python
def compose(self) -> ComposeResult:
    yield ListView(id="feeds-list")
    yield Static("", id="empty-message")
    yield Static("", id="error-message")
```

#### `on_mount() -> None`

Called when screen is mounted. Loads feeds and populates list.

**Behavior**:
- Loads feeds via `feed_manager.load_feeds()`
- Filters invalid entries (missing/invalid URLs)
- Sorts feeds alphabetically by name
- Resolves duplicate names for display
- Populates ListView with feed items
- Handles empty state (displays "No feeds saved" message)
- Handles errors gracefully (displays error message, allows return to menu)

**Side Effects**:
- Loads configuration file
- Caches feeds list in memory for session duration
- Updates screen widgets

**Example**:
```python
def on_mount(self) -> None:
    try:
        feeds = load_feeds()
        valid_feeds = self._filter_valid_feeds(feeds)
        sorted_feeds = self._sort_feeds(valid_feeds)
        display_feeds = self._resolve_duplicate_names(sorted_feeds)
        self._populate_list(display_feeds)
    except Exception as e:
        self._show_error(str(e))
```

#### `on_list_view_selected(event: ListView.Selected) -> None`

Handles feed selection from ListView.

**Parameters**:
- `event`: ListView.Selected event containing selected item

**Behavior**:
- Extracts Feed object from selected ListItem
- Transitions to watch action (future Story 4)
- For now: logs selection, shows placeholder message

**Example**:
```python
@on(ListView.Selected)
def on_list_view_selected(self, event: ListView.Selected) -> None:
    feed = event.item.id  # Feed object stored as item ID
    self.app.push_screen(WatchCamScreen(feed))  # Future Story 4
```

#### `action_return_to_menu() -> None`

Returns to main menu screen.

**Behavior**:
- Pops current screen
- Returns to MainMenuScreen

**Example**:
```python
def action_return_to_menu(self) -> None:
    self.app.pop_screen()
```

## Internal Methods (Implementation Details)

### `_filter_valid_feeds(feeds: list[Feed]) -> list[Feed]`

Filters out feeds with invalid or missing URLs.

**Parameters**:
- `feeds`: List of Feed objects

**Returns**: List of valid Feed objects

**Behavior**:
- Skips feeds with empty or None URLs
- Skips feeds with invalid URL format
- Logs skipped feeds via structured logging

### `_sort_feeds(feeds: list[Feed]) -> list[Feed]`

Sorts feeds alphabetically by name (case-insensitive).

**Parameters**:
- `feeds`: List of Feed objects

**Returns**: Sorted list of Feed objects

**Behavior**:
- Sorts by name.lower() for case-insensitive ordering
- Maintains stable sort (preserves order for equal names)

### `_resolve_duplicate_names(feeds: list[Feed]) -> list[Feed]`

Resolves duplicate feed names by adding number suffixes.

**Parameters**:
- `feeds`: List of Feed objects (already sorted)

**Returns**: List of Feed objects with resolved display names

**Behavior**:
- Checks for duplicate names
- Appends " (2)", " (3)", etc. to duplicates
- Returns feeds with resolved display names (display names not persisted)

### `_truncate_name(name: str, max_width: int) -> str`

Truncates feed name to fit terminal width.

**Parameters**:
- `name`: Feed name to truncate
- `max_width`: Maximum width in characters

**Returns**: Truncated name with ellipsis if needed

**Behavior**:
- Returns name as-is if within width
- Truncates to max_width - 3 and appends "..." if exceeds width

### `_populate_list(feeds: list[Feed]) -> None`

Populates ListView with feed items.

**Parameters**:
- `feeds`: List of Feed objects to display

**Behavior**:
- Creates ListItem for each feed
- Adds emoji icon and feed name to each item
- Stores Feed object as item ID for selection handling
- Shows empty message if no feeds

### `_show_empty_state() -> None`

Displays empty state message.

**Behavior**:
- Shows "No feeds saved" message
- Hides ListView
- Provides guidance on how to add feeds

### `_show_error(message: str) -> None`

Displays error message.

**Parameters**:
- `message`: Error message to display

**Behavior**:
- Shows error message
- Allows user to return to main menu
- Logs error via structured logging

## Data Types

### Feed (Reused)

Pydantic model from `pick_a_zoo.core.models.Feed`. See feed-manager contract for details.

## Error Handling

All errors are handled gracefully:
- **File read errors**: Display error message, allow return to menu
- **Invalid feed entries**: Skip silently, log warning
- **Empty feeds**: Display empty state message
- **Corrupted config**: Handled by feed_manager, displays recovered feeds or empty state

## Testing Contract

Unit tests must cover:
- Screen mounting and feed loading
- Invalid feed filtering
- Alphabetical sorting
- Duplicate name resolution
- Name truncation
- Empty state display
- Error handling
- Navigation (arrow keys, WASD)
- Feed selection
- Return to menu

Integration tests must cover:
- Screen integration with main menu
- Feed loading from actual YAML file
- ListView scrolling behavior
- Terminal resize handling

