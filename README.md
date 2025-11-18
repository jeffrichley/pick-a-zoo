# Pick-a-Zoo

A terminal-based camera feed viewer for watching live animal cams from zoos and wildlife centers.

## Installation

### Prerequisites

- Python 3.12 or higher
- Terminal supporting ANSI color codes
- Terminal size: 80x24 minimum (with graceful degradation)

### Install with uv

```bash
# Clone the repository
git clone <repository-url>
cd pick-a-zoo

# Install dependencies
uv sync

# Install the package
uv pip install -e .

# Install Playwright browsers (optional, for JavaScript-rendered pages)
uv run playwright install chromium
```

## Usage

### Launch the TUI

```bash
# After installation, run:
pickazoo

# Or directly with uv:
uv run pickazoo
```

### Navigation

- **Arrow keys (↑↓)** or **WASD (W/S)** - Navigate menu options
- **Enter** - Select highlighted option
- **Number keys (1-4)** - Direct selection via hotkeys
- **Letter hotkeys**:
  - `v` - View Saved Cams
  - `a` - Add a New Cam
  - `w` - Watch a Cam
  - `q` - Quit
- **q** or **Escape** - Quit application

### Menu Options

1. **View Saved Cams** - Browse your saved camera feeds
2. **Add a New Cam** - Add a new camera feed to your collection
3. **Watch a Cam** - Watch a camera feed
4. **Quit** - Exit the application

## Configuration

Camera feeds are stored in a YAML configuration file located in a local `.pickazoo` directory:

- **Location**: `.pickazoo/feeds.yaml` (relative to the current working directory)

The configuration file is automatically created on first run if it doesn't exist.

### Configuration File Format

```yaml
feeds:
  - name: "Panda Cam"
    url: "https://example.org/panda.m3u8"
    window_size:
      width: 1280
      height: 720
  - name: "Otter Live"
    url: "https://example.org/otter.mp4"
```

## Development

### Running Tests

```bash
# Run all tests
just test

# Run specific test file
uv run pytest tests/unit/test_feed_manager.py

# Run with coverage
uv run pytest --cov=src/pick_a_zoo
```

### Code Quality

```bash
# Linting
uv run ruff check src tests

# Type checking
uv run mypy src
```

## Features

- 🎨 Beautiful terminal user interface (TUI) built with Textual
- 📁 Cross-platform configuration file management
- 🔄 Graceful error handling for missing/corrupted config files
- ⌨️ Multiple navigation methods (arrow keys, WASD, hotkeys)
- 📊 Feed count display
- ⚠️ Terminal size warnings

## License

[Add your license here]
