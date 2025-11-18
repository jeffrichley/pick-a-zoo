# Quickstart: Launch the Pick-a-Zoo TUI

**Feature**: Launch the Pick-a-Zoo TUI
**Date**: 2024-12-19
**Phase**: 1 - Design & Contracts

## Overview

This guide provides a quick start for developers implementing the Pick-a-Zoo TUI launch feature. It covers the essential setup, key components, and basic usage patterns.

## Prerequisites

- Python 3.12+
- Dependencies installed via `uv` (see `pyproject.toml`)
- Terminal supporting ANSI color codes
- Terminal size: 80x24 minimum (with graceful degradation)

## Project Structure

```
src/pick_a_zoo/
├── cli.py                 # CLI entry point
├── core/
│   └── feed_manager.py    # Feed loading/saving library
└── tui/
    ├── app.py             # Textual App root
    └── screens/
        └── main_menu.py   # Main menu screen
```

## Key Components

### 1. CLI Entry Point (`cli.py`)

```python
from pick_a_zoo.tui.app import PickAZooApp

def main():
    """Entry point for pickazoo command."""
    app = PickAZooApp()
    app.run()

if __name__ == "__main__":
    main()
```

### 2. Feed Manager (`core/feed_manager.py`)

Standalone library for configuration file management:

```python
from pick_a_zoo.core.feed_manager import load_feeds, save_feeds, Feed

# Load feeds (creates file if missing)
feeds = load_feeds()

# Save feeds (atomic write)
save_feeds(feeds)
```

### 3. TUI App (`tui/app.py`)

Textual application root:

```python
from textual.app import App
from pick_a_zoo.tui.screens.main_menu import MainMenuScreen

class PickAZooApp(App):
    def on_mount(self):
        self.push_screen(MainMenuScreen())
```

### 4. Main Menu Screen (`tui/screens/main_menu.py`)

Menu display and navigation:

```python
from textual.screen import Screen
from pick_a_zoo.core.feed_manager import load_feeds

class MainMenuScreen(Screen):
    def on_mount(self):
        feeds = load_feeds()
        # Display menu with feed count
```

## Running the Application

### Development

```bash
# Install dependencies
uv sync

# Run application
uv run python -m pick_a_zoo.cli

# Or via entry point (after installation)
pickazoo
```

### Testing

```bash
# Run unit tests
just test

# Run specific test file
pytest tests/unit/test_feed_manager.py

# Run with coverage
pytest --cov=src/pick_a_zoo
```

## Development Workflow

### 1. Write Tests First (TDD)

Following Constitution Principle I (Test-First Development):

```python
# tests/unit/test_feed_manager.py
def test_load_feeds_missing_file():
    """Test that missing file creates empty file and returns empty list."""
    # Arrange
    # Act
    feeds = load_feeds()
    # Assert
    assert feeds == []
    assert config_file.exists()
```

### 2. Implement Library Module

```python
# src/pick_a_zoo/core/feed_manager.py
def load_feeds() -> list[Feed]:
    """Load feeds from YAML file."""
    # Implementation
```

### 3. Integrate with TUI

```python
# src/pick_a_zoo/tui/screens/main_menu.py
def on_mount(self):
    feeds = load_feeds()  # Use library
    # Display in TUI
```

## Key Patterns

### Error Handling

Always handle missing/corrupted config gracefully:

```python
try:
    feeds = load_feeds()
except Exception as e:
    logger.error(f"Failed to load feeds: {e}")
    feeds = []  # Fallback to empty list
```

### Structured Logging

Use loguru for all logging:

```python
from loguru import logger

logger.info("Loading feeds from config")
logger.warning("Config file corrupted, rebuilding")
logger.error("Failed to save feeds", exc_info=True)
```

### Atomic File Writes

Prevent corruption with atomic writes:

```python
import tempfile
import shutil

# Write to temp file first
with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
    yaml.dump(data, tmp)
    tmp_path = tmp.name

# Atomic rename
shutil.move(tmp_path, config_path)
```

## Common Tasks

### Adding a New Menu Option

1. Update `MainMenuScreen` menu list
2. Add key binding
3. Add action handler
4. Update tests

### Modifying Feed Structure

1. Update `Feed` Pydantic model
2. Update YAML schema documentation
3. Add migration logic if needed
4. Update tests

### Debugging TUI Issues

```python
# Enable Textual debug mode
app = PickAZooApp()
app.run(debug=True)
```

## Next Steps

After implementing Story 1:
- Story 2: Add a New Cam Feed
- Story 3: View Saved Cam Feeds
- Story 4: Launch Video Window

## Resources

- [Textual Documentation](https://textual.textualize.io/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [PyYAML Documentation](https://pyyaml.org/)
- [Platformdirs Documentation](https://platformdirs.readthedocs.io/)
