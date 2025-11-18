# Quick Start: Add a New Live Cam Feed

**Feature**: 002-add-cam-feed  
**Date**: 2024-12-19

## Overview

This guide provides a quick start for implementing the "Add a New Live Cam Feed" feature. The feature enables users to add camera feeds by providing a name and URL, with automatic detection of direct streams vs HTML pages containing embedded streams.

## Architecture Overview

The feature consists of three main components:

1. **Feed Discovery Library** (`core/feed_discovery.py`): Standalone library for URL detection, HTML parsing, and stream extraction
2. **Feed Manager Extension** (`core/feed_manager.py`): Extended with duplicate name resolution
3. **Add Feed Screen** (`tui/screens/add_feed.py`): TUI screen for the add feed workflow

## Implementation Steps

### Step 1: Create Feed Discovery Library

Create `src/pick_a_zoo/core/feed_discovery.py`:

```python
"""Feed discovery library for detecting URLs and extracting streams."""

from enum import Enum
from dataclasses import dataclass
import httpx
from bs4 import BeautifulSoup
from loguru import logger

class URLType(Enum):
    DIRECT_STREAM = "direct_stream"
    HTML_PAGE = "html_page"

@dataclass
class StreamCandidate:
    url: str
    source_type: str

@dataclass
class URLValidationResult:
    is_accessible: bool
    status_code: int | None = None
    error_message: str | None = None
    content_type: str | None = None

def detect_url_type(url: str) -> URLType:
    """Detect if URL is direct stream or HTML page."""
    # Implementation: pattern matching + HTTP HEAD request
    pass

def extract_streams_from_html(html_content: str, base_url: str) -> list[StreamCandidate]:
    """Extract stream URLs from HTML content."""
    # Implementation: BeautifulSoup parsing
    pass

def validate_url_accessibility(url: str, timeout: float = 15.0) -> URLValidationResult:
    """Validate URL accessibility."""
    # Implementation: HTTP HEAD request
    pass
```

### Step 2: Extend Feed Manager

Add to `src/pick_a_zoo/core/feed_manager.py`:

```python
def resolve_duplicate_name(name: str, existing_feeds: list[Feed]) -> str:
    """Resolve duplicate feed names by appending number suffix."""
    # Implementation: check existing names, append (2), (3), etc.
    pass
```

### Step 3: Create Add Feed Screen

Create `src/pick_a_zoo/tui/screens/add_feed.py`:

```python
"""Add feed screen for TUI."""

from textual.screen import Screen
from textual.widgets import Input, ListView
from pick_a_zoo.core.feed_discovery import detect_url_type, extract_streams_from_html, validate_url_accessibility
from pick_a_zoo.core.feed_manager import load_feeds, save_feeds, resolve_duplicate_name
from pick_a_zoo.core.models import Feed

class AddFeedScreen(Screen):
    """Screen for adding new camera feeds."""
    
    def compose(self):
        # Implementation: Textual widgets for name/URL input
        pass
    
    def on_input_submitted(self, name: str):
        # Implementation: handle name input
        pass
    
    def on_url_submitted(self, url: str):
        # Implementation: handle URL input, detect type, extract streams
        pass
```

### Step 4: Integrate with Main Menu

Update `src/pick_a_zoo/tui/screens/main_menu.py`:

```python
def on_add_cam_selected(self):
    """Handle 'Add Cam' menu selection."""
    self.app.push_screen(AddFeedScreen())
```

## Testing Strategy

### Unit Tests

1. **test_feed_discovery.py**:
   - Test URL type detection (direct stream vs HTML)
   - Test stream extraction from HTML
   - Test URL validation
   - Test error handling

2. **test_feed_manager.py** (extend existing):
   - Test duplicate name resolution
   - Test integration with save_feeds()

3. **test_add_feed.py**:
   - Test screen workflow
   - Test input validation
   - Test error handling

### Integration Tests

1. **test_feed_discovery_integration.py**:
   - Test end-to-end feed discovery workflow
   - Test with real HTML pages (mocked)
   - Test with real URLs (network tests, marked slow)

## Key Implementation Details

### URL Detection

- Pattern matching first (fast): check for .m3u8, .mp4, .webm, rtsp://
- HTTP HEAD fallback: check Content-Type header
- Follow redirects (up to 5)

### HTML Parsing

- Use BeautifulSoup4 with lxml backend
- Extract from `<video>` and `<source>` tags
- Search for m3u8 links in page content
- Basic iframe support (deferred: full player API integration)

### Duplicate Name Resolution

- Check existing feed names
- Append " (2)", " (3)", etc. until unique
- Increment number until no conflict

### Error Handling

- User-friendly error messages
- Retry options for network errors
- Cancellation at any point
- Structured logging for debugging

## Dependencies

All dependencies are already in `pyproject.toml`:
- `httpx` - HTTP client
- `beautifulsoup4` - HTML parsing
- `lxml` - HTML parser backend
- `textual` - TUI framework
- `pydantic` - Data validation
- `loguru` - Structured logging

## Next Steps

1. Write unit tests first (TDD)
2. Implement feed_discovery.py
3. Extend feed_manager.py with duplicate resolution
4. Implement add_feed.py screen
5. Integrate with main menu
6. Write integration tests
7. Manual testing with real URLs

## References

- [Feed Discovery Contract](./contracts/feed-discovery.md)
- [Feed Manager Extension Contract](./contracts/feed-manager-extension.md)
- [Add Feed Screen Contract](./contracts/add-feed-screen.md)
- [Data Model](./data-model.md)
- [Research Findings](./research.md)

