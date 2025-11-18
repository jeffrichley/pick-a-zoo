# Data Model: Add a New Live Cam Feed

**Feature**: 002-add-cam-feed  
**Date**: 2024-12-19  
**Phase**: 1 - Design & Contracts

## Validation Guidelines

**Note**: When implementing Pydantic models, prefer field validation over classmethod validators whenever possible. Field validators (`@field_validator`) are simpler, more explicit, and easier to test than classmethod validators (`@model_validator`). Use classmethod validators only when validation requires access to multiple fields or complex cross-field validation logic.

**Examples**:
- ✅ **Preferred**: `@field_validator("name")` for validating a single field
- ❌ **Avoid**: `@model_validator(mode="before")` for single-field validation
- ✅ **Acceptable**: `@model_validator(mode="after")` when validation requires multiple fields

## Entities

### Feed (Existing, Extended)

**Source**: `src/pick_a_zoo/core/models.py`

**Description**: Represents a single live camera feed entry. Already defined in Story 1, no changes required for this feature.

**Fields**:
- `name: str` - User-provided identifier (required, non-empty, whitespace-stripped)
- `url: HttpUrl` - Direct stream URL or extracted stream URL (required, validated URL)
- `window_size: WindowSize | None` - Optional preferred display dimensions

**Validation Rules**:
- Name must be non-empty after stripping whitespace
- URL must be valid HTTP/HTTPS URL (Pydantic HttpUrl validation)
- Window size must have width > 0 and height > 0 if provided

**State Transitions**: None (immutable data structure)

**Relationships**: 
- Contained in `FeedsConfigurationFile.feeds` list
- Referenced by `FeedDiscoveryResult` when extracted from HTML

### FeedsConfigurationFile (Existing)

**Source**: Managed by `src/pick_a_zoo/core/feed_manager.py`

**Description**: Represents the persisted collection of all saved cam feeds. Stored as feeds.yaml file.

**Structure**:
```yaml
feeds:
  - name: "Panda Cam"
    url: "https://example.org/panda.m3u8"
    window_size:
      width: 1280
      height: 720
  - name: "Otter Live"
    url: "https://example.org/otter_stream.mp4"
```

**Operations**:
- `load_feeds()` - Load feeds from YAML file
- `save_feeds(feeds: list[Feed])` - Save feeds to YAML file (atomic write)
- **NEW**: `resolve_duplicate_name(name: str, existing_feeds: list[Feed]) -> str` - Resolve duplicate names by appending number suffix

**Validation Rules**:
- YAML structure must be valid
- `feeds` must be a list
- Each feed entry must be valid Feed object
- File must be readable/writable (platformdirs location)

**State Transitions**:
- Empty → Populated (when feeds added)
- Populated → Modified (when feeds added/modified)
- Corrupted → Recovered (when corruption detected, file rebuilt)

### FeedDiscoveryResult (New)

**Source**: `src/pick_a_zoo/core/feed_discovery.py`

**Description**: Represents the result of discovering streams from a URL.

**Fields**:
- `url_type: URLType` - Enum: DIRECT_STREAM or HTML_PAGE
- `streams: list[StreamCandidate]` - List of discovered stream URLs (empty if direct stream, populated if HTML page)
- `original_url: str` - Original URL provided by user

**Usage**: Returned by feed discovery functions to indicate what was found.

### StreamCandidate (New)

**Source**: `src/pick_a_zoo/core/feed_discovery.py`

**Description**: Represents a candidate stream URL extracted from HTML.

**Fields**:
- `url: str` - Extracted stream URL
- `source_type: str` - How it was found ("video_tag", "source_tag", "m3u8_link", "iframe")

**Usage**: Used when multiple streams are found, presented to user for selection.

### URLValidationResult (New)

**Source**: `src/pick_a_zoo/core/feed_discovery.py`

**Description**: Represents the result of validating a URL's accessibility.

**Fields**:
- `is_accessible: bool` - Whether URL is accessible
- `status_code: int | None` - HTTP status code if available
- `error_message: str | None` - Error message if validation failed
- `content_type: str | None` - Content-Type header if available

**Usage**: Returned by URL validation functions to indicate accessibility status.

## Enumerations

### URLType (New)

**Source**: `src/pick_a_zoo/core/feed_discovery.py`

**Values**:
- `DIRECT_STREAM` - URL is a direct stream (m3u8, mp4, webm, rtsp, etc.)
- `HTML_PAGE` - URL is an HTML webpage containing embedded streams

## Functions & Operations

### Feed Discovery Functions

**Module**: `src/pick_a_zoo/core/feed_discovery.py`

#### `detect_url_type(url: str) -> URLType`
Detects whether URL is a direct stream or HTML page.

**Input**: URL string
**Output**: URLType enum
**Errors**: Raises `FeedDiscoveryError` if detection fails

#### `extract_streams_from_html(html_content: str, base_url: str) -> list[StreamCandidate]`
Extracts stream URLs from HTML content.

**Input**: HTML content string, base URL for resolving relative URLs
**Output**: List of StreamCandidate objects
**Errors**: Raises `HTMLParseError` if parsing fails

#### `validate_url_accessibility(url: str, timeout: float = 15.0) -> URLValidationResult`
Validates that a URL is accessible.

**Input**: URL string, timeout in seconds
**Output**: URLValidationResult
**Errors**: Raises `URLValidationError` if validation fails

### Feed Manager Extensions

**Module**: `src/pick_a_zoo/core/feed_manager.py`

#### `resolve_duplicate_name(name: str, existing_feeds: list[Feed]) -> str`
Resolves duplicate feed names by appending number suffix.

**Input**: Proposed name, list of existing feeds
**Output**: Resolved unique name (e.g., "Panda Cam (2)")
**Logic**: 
- If name is unique, return as-is
- If duplicate, append " (2)", " (3)", etc. until unique

## Data Flow

### Add Direct Stream Flow
1. User provides name and URL
2. `detect_url_type()` → `DIRECT_STREAM`
3. `validate_url_accessibility()` → check accessibility
4. If valid: create Feed object, resolve duplicate name, save via `save_feeds()`

### Add HTML Page Flow
1. User provides name and URL
2. `detect_url_type()` → `HTML_PAGE`
3. `validate_url_accessibility()` → check accessibility
4. Fetch HTML content
5. `extract_streams_from_html()` → list of StreamCandidate
6. If single stream: auto-select, create Feed, resolve duplicate name, save
7. If multiple streams: present list to user, user selects, create Feed, resolve duplicate name, save

## Constraints & Invariants

1. **Feed Name Uniqueness**: After duplicate resolution, all feed names in feeds.yaml must be unique
2. **URL Validation**: All saved feeds must have validated accessible URLs (except authentication, which is deferred)
3. **Atomic Writes**: Feed saves must be atomic (write to temp file, then rename)
4. **YAML Validity**: feeds.yaml must always be valid YAML, even if corrupted (rebuilt as empty)

## Error Handling

### FeedDiscoveryError
Raised when feed discovery fails (network error, parsing error, etc.)

### URLValidationError
Raised when URL validation fails (timeout, connection error, etc.)

### HTMLParseError
Raised when HTML parsing fails (malformed HTML, encoding issues, etc.)

All errors include user-friendly messages and context for logging.

