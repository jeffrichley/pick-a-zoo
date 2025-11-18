# Research: Add a New Live Cam Feed

**Feature**: 002-add-cam-feed
**Date**: 2024-12-19
**Phase**: 0 - Outline & Research

## Research Tasks & Findings

### 1. URL Detection: Direct Stream vs HTML Page

**Task**: Determine how to detect whether a URL is a direct stream or an HTML webpage.

**Decision**: Use URL extension/pattern matching for direct streams, HTTP HEAD/GET request for HTML detection.

**Rationale**:
- Direct stream URLs typically have recognizable extensions (.m3u8, .mp4, .webm) or protocols (rtsp://)
- HTTP HEAD request can check Content-Type header to distinguish HTML pages from media streams
- Pattern matching is fast and reliable for common stream formats
- Falls back to fetching content if pattern matching is inconclusive

**Alternatives Considered**:
- **Always fetch and check Content-Type**: More reliable but slower, requires network request for all URLs
- **Regex-only pattern matching**: Fastest but may miss edge cases, doesn't handle redirects
- **Chosen approach**: Balance of speed (pattern matching first) and reliability (HTTP request fallback)

**Implementation Notes**:
- Check URL extension/pattern first (m3u8, mp4, webm, rtsp://, etc.)
- If pattern matches known stream format → treat as direct stream
- If pattern doesn't match → perform HTTP HEAD request to check Content-Type
- If Content-Type is text/html → treat as HTML page
- If Content-Type is video/* or application/vnd.apple.mpegurl → treat as direct stream
- Handle redirects (follow up to 5 redirects)

### 2. HTML Parsing for Video Stream Extraction

**Task**: Determine how to extract embedded video stream URLs from HTML pages.

**Decision**: Use BeautifulSoup4 with lxml backend to parse HTML and extract video sources.

**Rationale**:
- BeautifulSoup4 is already in tech stack, well-maintained, and handles malformed HTML gracefully
- lxml backend provides faster parsing and better error handling than default html.parser
- Can extract from multiple sources: `<video>` tags, `<source>` tags, m3u8 links in page content, embedded player iframes
- Supports CSS selectors for flexible extraction patterns

**Alternatives Considered**:
- **regex-only extraction**: Too fragile, doesn't handle nested HTML properly
- **Selenium/Playwright for JavaScript rendering**: Overkill for initial implementation, adds significant complexity and dependencies
- **Chosen approach**: Static HTML parsing covers 90% of use cases (SC-004), JavaScript-rendered content deferred to future enhancement

**Implementation Notes**:
- Parse HTML with BeautifulSoup4 (lxml backend)
- Extract from `<video>` tags: look for `src` attribute and `<source>` children
- Extract from `<source>` tags: look for `src` and `srcset` attributes
- Search page content for m3u8 URLs (regex pattern for .m3u8 links)
- Extract from embedded iframes: check common video player domains (YouTube, Vimeo, etc.) - basic support only
- Filter out non-stream URLs (images, static files)
- Return list of candidate stream URLs

### 3. Stream URL Validation

**Task**: Determine how to validate that extracted stream URLs are accessible and playable.

**Decision**: Perform HTTP HEAD request with timeout (10-30 seconds) to check accessibility, skip authentication validation.

**Rationale**:
- HTTP HEAD is lightweight (doesn't download content) and sufficient for accessibility check
- Timeout prevents hanging on slow/unresponsive URLs
- Authentication validation deferred to playback time (per clarification)
- Non-200 status codes indicate inaccessible URLs
- Network errors handled gracefully with retry options

**Alternatives Considered**:
- **Full GET request**: More reliable but wastes bandwidth, slower
- **No validation**: Faster but allows invalid feeds to be saved
- **Chosen approach**: Balance of validation thoroughness and performance

**Implementation Notes**:
- Use httpx with timeout (configurable, default 15 seconds)
- Follow redirects (up to 5 redirects)
- Check HTTP status code (200-299 = accessible, others = error)
- Handle network errors (timeout, connection refused, DNS failure)
- Return validation result with error details if failed

### 4. Duplicate Feed Name Handling

**Task**: Determine how to handle duplicate feed names when saving.

**Decision**: Auto-append number suffix (e.g., "Panda Cam (2)", "Panda Cam (3)") when duplicate detected.

**Rationale**:
- Per clarification: user selected auto-append approach
- Prevents accidental overwrites
- Allows users to have multiple feeds with similar names
- Simple and predictable behavior

**Alternatives Considered**:
- **Reject duplicates**: Too restrictive, requires user to remember all existing names
- **Prompt for rename**: Adds friction, interrupts workflow
- **Allow duplicates**: Confusing, makes feed selection ambiguous
- **Chosen approach**: Automatic resolution balances user convenience and data integrity

**Implementation Notes**:
- Check existing feed names when saving
- If duplicate found, append " (2)", " (3)", etc. until unique name found
- Increment number until no conflict exists
- Save feed with resolved name

### 5. Multiple Stream Selection UI

**Task**: Determine how to present multiple stream options to users in TUI.

**Decision**: Display list showing user-provided feed name for each stream option, allow selection via arrow keys.

**Rationale**:
- Per clarification: display user-provided feed name for each option
- Textual framework provides built-in list widgets
- Arrow key navigation consistent with main menu UX
- Simple and intuitive for users

**Alternatives Considered**:
- **Show stream URLs**: Too technical, URLs can be very long
- **Show stream metadata**: Requires additional parsing, may not be available
- **Chosen approach**: Use feed name as identifier, simple and user-friendly

**Implementation Notes**:
- Use Textual ListView widget
- Display feed name for each stream option
- Allow navigation with arrow keys
- Confirm selection with Enter key
- Allow cancellation with Escape or 'q' key

### 6. Error Handling Patterns

**Task**: Determine error handling patterns for network failures, parsing errors, and validation failures.

**Decision**: Use structured error types with user-friendly messages, graceful degradation, retry options.

**Rationale**:
- Clear error messages improve user experience (SC-006)
- Retry options allow recovery from transient failures (SC-007)
- Graceful degradation prevents crashes (SC-009)
- Structured errors enable better logging and debugging

**Implementation Notes**:
- Define custom exception types: `FeedDiscoveryError`, `URLValidationError`, `HTMLParseError`
- Map technical errors to user-friendly messages
- Provide retry option for network errors
- Allow cancellation at any point
- Log errors with context for debugging

## Dependencies & Integration Points

### Existing Components
- **feed_manager.py**: Extend `save_feeds()` to handle duplicate name resolution
- **models.py**: Feed model already supports name and url fields
- **main_menu.py**: Add "Add Cam" option that navigates to AddFeedScreen

### New Components
- **feed_discovery.py**: New library module for URL detection and stream extraction
- **add_feed.py**: New TUI screen for add feed workflow

### External Libraries
- **httpx**: HTTP client for URL validation and HTML fetching
- **beautifulsoup4**: HTML parsing for stream extraction
- **lxml**: HTML parser backend (faster, more robust)
- **m3u8**: HLS playlist parsing (if needed for multi-variant streams)

## Open Questions Resolved

1. ✅ **URL detection approach**: Pattern matching + HTTP HEAD request
2. ✅ **HTML parsing approach**: BeautifulSoup4 with lxml backend
3. ✅ **Stream validation**: HTTP HEAD with timeout, skip auth
4. ✅ **Duplicate handling**: Auto-append number suffix
5. ✅ **Multiple stream UI**: List with feed name, arrow key selection
6. ✅ **Error handling**: Structured errors, user-friendly messages, retry options

## Deferred Decisions

- **JavaScript-rendered content**: Deferred to future enhancement (edge case, low priority)
- **Advanced iframe extraction**: Basic support only, full player API integration deferred
- **Stream quality detection**: Not required for initial implementation
- **Rate limiting**: Not required for single-user desktop application

## References

- httpx documentation: https://www.python-httpx.org/
- BeautifulSoup4 documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- Textual documentation: https://textual.textualize.io/
- m3u8 library: https://github.com/globocom/m3u8
