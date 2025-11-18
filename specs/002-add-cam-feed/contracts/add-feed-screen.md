# Add Feed Screen Contract

**Module**: `pick_a_zoo.tui.screens.add_feed`
**Type**: TUI Screen Component
**Constitution**: Library-First Architecture (Principle II) - Screen is modular and self-contained

## Overview

The Add Feed Screen is a Textual screen component that provides the user interface for adding new camera feeds. It handles the complete workflow: prompting for name and URL, detecting URL type, extracting streams from HTML if needed, validating URLs, and saving feeds.

## Interface

### `AddFeedScreen` (Class)

Textual Screen component for adding feeds.

**Inherits from**: `textual.screen.Screen`

**Methods**:

#### `on_mount() -> None`

Called when screen is mounted. Initializes the screen state and displays initial prompt.

**Behavior**:
- Displays prompt for feed name
- Sets up input fields and navigation
- Initializes state variables

#### `on_input_submitted(name: str) -> None`

Handles feed name input submission.

**Parameters**:
- `name` (str): User-provided feed name

**Behavior**:
- Validates name (non-empty, stripped)
- Stores name in screen state
- Prompts for URL input

**Raises**:
- Displays error message if name is invalid

#### `on_url_submitted(url: str) -> None`

Handles URL input submission and initiates feed discovery process.

**Parameters**:
- `url` (str): User-provided URL

**Behavior**:
- Validates URL format
- Displays "Validating..." message
- Calls `detect_url_type()` to determine URL type
- If direct stream: validates accessibility, saves feed
- If HTML page: fetches HTML, extracts streams, handles single/multiple streams
- Shows error messages if validation fails
- Allows retry or cancellation

**Side Effects**:
- Performs network I/O (URL validation, HTML fetching)
- Updates UI with progress messages
- Saves feed to configuration file if successful

#### `on_stream_selected(stream_index: int) -> None`

Handles user selection from multiple stream options.

**Parameters**:
- `stream_index` (int): Index of selected stream in list

**Behavior**:
- Retrieves selected stream URL
- Creates Feed object with user-provided name and selected URL
- Resolves duplicate name
- Saves feed
- Returns to main menu

#### `on_cancel() -> None`

Handles cancellation of feed addition process.

**Behavior**:
- Returns to main menu without saving
- Clears any entered data
- Does not lose user's place in application

## User Interaction Flow

1. **Name Entry**:
   - User enters feed name
   - System validates and stores name
   - Prompts for URL

2. **URL Entry**:
   - User enters URL
   - System validates URL format
   - System detects URL type (direct stream or HTML page)

3. **Direct Stream Path**:
   - System validates URL accessibility
   - If valid: creates Feed, resolves duplicate name, saves, returns to menu
   - If invalid: displays error, allows retry or cancel

4. **HTML Page Path**:
   - System fetches HTML content
   - System extracts stream URLs
   - If single stream: auto-selects, creates Feed, resolves duplicate name, saves
   - If multiple streams: displays list, user selects, creates Feed, resolves duplicate name, saves
   - If no streams: displays error, allows retry or cancel

## Error Handling

- **Invalid Name**: Display error message, allow re-entry
- **Invalid URL Format**: Display error message, allow re-entry
- **Network Error**: Display error message with retry option
- **URL Not Accessible**: Display error message with retry/cancel options
- **No Streams Found**: Display error message, prompt to try another URL
- **Save Error**: Display error message, allow retry

All errors are user-friendly and actionable.

## Navigation

- **Arrow Keys**: Navigate list of stream options (when multiple streams found)
- **Enter**: Confirm selection or submit input
- **Escape / 'q'**: Cancel and return to main menu
- **Tab**: Move between input fields

## Dependencies

- `feed_discovery`: URL detection, stream extraction, URL validation
- `feed_manager`: Feed loading/saving, duplicate name resolution
- `models`: Feed data model

## Testing Contract

Unit tests must cover:
- Name input validation
- URL input validation
- Direct stream workflow (success and error cases)
- HTML page workflow (single stream, multiple streams, no streams)
- Stream selection from list
- Error handling and retry logic
- Cancellation at various points
- Duplicate name resolution integration
