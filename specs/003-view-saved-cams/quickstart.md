# Quickstart: View Saved Cam Feeds in TUI

**Feature**: View Saved Cam Feeds in TUI
**Date**: 2024-12-19
**Phase**: 1 - Design & Contracts

## Overview

This guide provides a quick start for developers implementing the View Saved Cam Feeds feature. It covers the essential setup, key components, and basic usage patterns.

## Prerequisites

- Python 3.12+
- Dependencies installed via `uv` (see `pyproject.toml`)
- Terminal supporting ANSI color codes
- Terminal size: 80x24 minimum (with graceful degradation)
- Existing feed_manager library (from Story 1)
- Existing Feed model (from Story 1)

## Project Structure

```
src/pick_a_zoo/
├── cli.py                 # CLI entry point
├── core/
│   ├── feed_manager.py    # Feed loading library (existing, reused)
│   └── models.py          # Feed model (existing, reused)
└── tui/
    ├── app.py             # Textual App root
    └── screens/
        ├── main_menu.py   # Main menu screen (existing, routes to new screen)
        └── view_saved_cams.py  # NEW: View saved cams screen
```

## Key Components

### 1. View Saved Cams Screen (`tui/screens/view_saved_cams.py`)

New Textual screen for displaying feeds list:

```python
from textual.screen import Screen
from textual.widgets import ListView, ListItem, Label, Static
from pick_a_zoo.core.feed_manager import load_feeds

class ViewSavedCamsScreen(Screen):
    BINDINGS = [
        ("escape", "return_to_menu", "Back"),
        ("q", "return_to_menu", "Back"),
    ]

    def compose(self):
        yield ListView(id="feeds-list")
        yield Static("", id="empty-message")

    def on_mount(self):
        feeds = load_feeds()
        valid_feeds = self._filter_valid_feeds(feeds)
        sorted_feeds = self._sort_feeds(valid_feeds)
        self._populate_list(sorted_feeds)
```

### 2. Feed Manager Integration (Reused)

Uses existing `feed_manager.load_feeds()` function:

```python
from pick_a_zoo.core.feed_manager import load_feeds

# Load feeds (handles missing/corrupted files automatically)
feeds = load_feeds()
# Returns: [Feed(name="Panda Cam", url="..."), ...]
# Or: [] if file missing/corrupted
```

### 3. Main Menu Integration

Update main menu to route to new screen:

```python
# In main_menu.py
elif option == "view":
    self.app.push_screen(ViewSavedCamsScreen())
```

## Running the Application

### Development

```bash
# Install dependencies
uv sync

# Run application
uv run python -m pick_a_zoo.cli

# Navigate to "View Saved Cams" option
```

### Testing

```bash
# Run unit tests
pytest tests/unit/test_view_saved_cams.py

# Run integration tests
pytest tests/integration/test_tui_integration.py

# Run with coverage
pytest --cov=src/pick_a_zoo --cov=tests
```

## Development Workflow

### 1. Write Tests First (TDD)

Following Constitution Principle I (Test-First Development):

```python
# tests/unit/test_view_saved_cams.py
def test_load_and_display_feeds():
    """Test that feeds are loaded and displayed correctly."""
    # Arrange
    feeds = [Feed(name="Panda Cam", url="https://example.com/panda.m3u8")]
    # Mock load_feeds to return feeds

    # Act
    screen = ViewSavedCamsScreen()
    screen.on_mount()

    # Assert
    list_view = screen.query_one("#feeds-list", ListView)
    assert len(list_view.children) == 1
```

### 2. Implement Screen Component

```python
# src/pick_a_zoo/tui/screens/view_saved_cams.py
class ViewSavedCamsScreen(Screen):
    def on_mount(self):
        feeds = load_feeds()  # Use existing library
        # Filter, sort, and display
```

### 3. Integrate with Main Menu

```python
# src/pick_a_zoo/tui/screens/main_menu.py
def action_select_view(self):
    self.app.push_screen(ViewSavedCamsScreen())
```

## Key Patterns

### Feed Loading Pattern

Load feeds once on screen mount, cache for session:

```python
def on_mount(self):
    try:
        feeds = load_feeds()  # Load from YAML
        self._feeds = self._prepare_feeds(feeds)  # Cache
        self._populate_list(self._feeds)
    except Exception as e:
        logger.error(f"Failed to load feeds: {e}")
        self._show_error("Failed to load feeds")
```

### Invalid Feed Filtering

Skip feeds with invalid or missing URLs:

```python
def _filter_valid_feeds(self, feeds: list[Feed]) -> list[Feed]:
    valid = []
    for feed in feeds:
        if feed.url and self._is_valid_url(feed.url):
            valid.append(feed)
        else:
            logger.warning(f"Skipping feed with invalid URL: {feed.name}")
    return valid
```

### Duplicate Name Resolution

Resolve duplicates for display (not persisted):

```python
def _resolve_duplicate_names(self, feeds: list[Feed]) -> list[tuple[Feed, str]]:
    """Returns list of (feed, display_name) tuples."""
    name_counts = {}
    result = []

    for feed in feeds:
        base_name = feed.name
        if base_name in name_counts:
            name_counts[base_name] += 1
            display_name = f"{base_name} ({name_counts[base_name]})"
        else:
            name_counts[base_name] = 1
            display_name = base_name
        result.append((feed, display_name))

    return result
```

### Name Truncation

Truncate long names to fit terminal width:

```python
def _truncate_name(self, name: str, max_width: int) -> str:
    if len(name) <= max_width:
        return name
    return name[:max_width - 3] + "..."
```

### Empty State Handling

Display friendly message when no feeds:

```python
def _show_empty_state(self):
    empty_msg = self.query_one("#empty-message", Static)
    empty_msg.update("No feeds saved. Use 'Add a New Cam' to add feeds.")
    empty_msg.visible = True

    list_view = self.query_one("#feeds-list", ListView)
    list_view.visible = False
```

### Error Handling

Handle errors gracefully:

```python
def on_mount(self):
    try:
        feeds = load_feeds()
        # ... process feeds
    except PermissionError as e:
        logger.error(f"Permission denied: {e}")
        self._show_error("Cannot read configuration file. Check permissions.")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        self._show_error("Failed to load feeds. Please try again.")
```

## Common Tasks

### Adding Feed Display Formatting

1. Modify `_populate_list()` to format feed items
2. Add emoji icons or styling
3. Update tests

### Handling Terminal Resize

Textual handles this automatically, but you can customize:

```python
def on_resize(self):
    # Recalculate name truncation width
    self._update_list_display()
```

### Adding Feed Details

To show more info (e.g., URL preview):

1. Extend ListItem to show multiple lines
2. Add tooltip or detail view
3. Update display logic

## Integration Points

### With Main Menu

```python
# main_menu.py
def action_select_view(self):
    self.app.push_screen(ViewSavedCamsScreen())
```

### With Feed Manager

```python
# Uses existing load_feeds() function
from pick_a_zoo.core.feed_manager import load_feeds

feeds = load_feeds()
```

### With Watch Action (Future Story 4)

```python
# view_saved_cams.py
@on(ListView.Selected)
def on_feed_selected(self, event):
    feed = event.item.id  # Feed object
    self.app.push_screen(WatchCamScreen(feed))  # Future Story 4
```

## Testing Strategies

### Unit Tests

Test screen logic independently:

```python
def test_filter_invalid_feeds():
    feeds = [
        Feed(name="Valid", url="https://example.com/valid.m3u8"),
        Feed(name="Invalid", url=""),  # Empty URL
    ]
    screen = ViewSavedCamsScreen()
    valid = screen._filter_valid_feeds(feeds)
    assert len(valid) == 1
    assert valid[0].name == "Valid"
```

### Integration Tests

Test screen integration:

```python
def test_screen_navigation():
    app = PickAZooApp()
    app.push_screen(ViewSavedCamsScreen())
    # Test navigation, selection, etc.
```

### Snapshot Tests

Test TUI layout:

```python
def test_screen_layout(snap_compare):
    screen = ViewSavedCamsScreen()
    assert snap_compare(screen)
```

## Next Steps

After implementing Story 3:
- Story 4: Launch Video Window for Selected Cam
- Story 5: Take a Snapshot of the Live Feed

## Resources

- [Textual ListView Documentation](https://textual.textualize.io/widgets/list_view/)
- [Textual Screen Documentation](https://textual.textualize.io/guide/screens/)
- [Feed Manager Contract](../001-launch-tui/contracts/feed-manager.md)
- [Existing Main Menu Implementation](../001-launch-tui/)
