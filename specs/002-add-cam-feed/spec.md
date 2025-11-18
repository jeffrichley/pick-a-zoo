# Feature Specification: Add a New Live Cam Feed

**Feature Branch**: `002-add-cam-feed`
**Created**: 2024-12-19
**Status**: Draft
**Input**: User description: "read files in the plan directory. we are working on the story Story 2 — Add a New Live Cam Feed. @s2-specify.md"

## Clarifications

### Session 2024-12-19

- Q: How should the system handle duplicate feed names when saving a new feed? → A: Auto-append number suffix (e.g., "Panda Cam", "Panda Cam (2)", "Panda Cam (3)")
- Q: When should the system validate URL accessibility during the feed addition process? → A: Validate immediately after URL entry
- Q: What information should be displayed to help users select from multiple streams? → A: Display the user-provided feed name for each stream option
- Q: How should the system handle URLs that require authentication or have access restrictions? → A: Skip validation during feed addition, attempt to save anyway, let playback fail later

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add Direct Stream Feed (Priority: P1)

As a user, I want to add a new cam feed by providing a name and a direct stream URL so that I can watch live animal cameras from any publicly available stream source.

**Why this priority**: This is the core functionality that enables users to personalize their Pick-a-Zoo experience. Adding direct stream feeds is the most straightforward use case and must work reliably before handling more complex HTML page scenarios. This delivers immediate value by allowing users to add any direct stream URL (m3u8, mp4, webm, rtsp, etc.) without requiring web page parsing.

**Independent Test**: Can be fully tested by providing a direct stream URL and verifying the feed is saved and appears in the saved feeds list. This delivers immediate value by enabling users to add any direct stream source.

**Acceptance Scenarios**:

1. **Given** the user is in the TUI main menu, **When** the user selects "Add Cam", **Then** the system prompts for a cam name
2. **Given** the user has entered a cam name, **When** the user enters a direct stream URL (e.g., .m3u8, .mp4, .webm, rtsp://), **Then** the system validates URL accessibility immediately, detects it as a direct stream, and saves it if valid
3. **Given** a direct stream URL has been detected and saved, **When** the user returns to the main menu, **Then** the newly added cam appears in the saved feeds list
4. **Given** the user enters an invalid or malformed URL, **When** the system validates the URL immediately after entry, **Then** the system displays a clear error message and allows the user to retry or cancel
5. **Given** the user enters a URL that is not accessible (network error, 404, etc.), **When** the system validates the URL immediately after entry, **Then** the system displays a clear error message explaining the issue and allows the user to retry or cancel

---

### User Story 2 - Add Feed from HTML Page (Priority: P2)

As a user, I want to add a cam feed by providing a webpage URL so that the system can automatically discover and extract embedded video streams from HTML pages.

**Why this priority**: This extends the core functionality to handle common scenarios where users find streams embedded in web pages rather than direct URLs. While not as critical as direct streams, this significantly enhances user experience by reducing manual work and demonstrates robust feed discovery capabilities.

**Independent Test**: Can be fully tested by providing an HTML page URL containing embedded video players and verifying the system extracts and saves the stream. This delivers value by enabling users to add feeds from web pages without manually extracting stream URLs.

**Acceptance Scenarios**:

1. **Given** the user enters a webpage URL (http/https), **When** the system validates URL accessibility immediately after entry, **Then** the system detects it as an HTML page and fetches the page content if accessible
2. **Given** an HTML page has been fetched, **When** the system parses the HTML, **Then** the system identifies embedded video sources (video tags, m3u8 links, embedded player URLs)
3. **Given** a single playable stream is found in the HTML, **When** the system extracts the stream URL, **Then** the system automatically selects it and saves the feed
4. **Given** multiple playable streams are found in the HTML, **When** the system extracts all stream URLs, **Then** the system presents a list showing the user-provided feed name for each stream option, allowing the user to select one
5. **Given** the user selects a stream from the list, **When** the user confirms the selection, **Then** the system saves the feed with the selected stream URL
6. **Given** no playable streams are found in the HTML, **When** the system completes parsing, **Then** the system displays a clear error message and prompts the user to try another URL

---

### User Story 3 - Handle Network and Validation Errors (Priority: P3)

As a user, I want clear error messages when adding feeds fails so that I understand what went wrong and can take appropriate action.

**Why this priority**: Error handling ensures a robust user experience and prevents frustration when feeds cannot be added. While not the primary feature, proper error handling is essential for user satisfaction and system reliability.

**Independent Test**: Can be fully tested by simulating various error conditions (network failures, invalid URLs, inaccessible pages) and verifying appropriate error messages are displayed. This delivers value by providing a smooth, predictable experience even when things go wrong.

**Acceptance Scenarios**:

1. **Given** the user attempts to add a feed, **When** there is no internet connection, **Then** the system displays a clear message indicating network connectivity issues and offers a retry option
2. **Given** the user enters a URL that times out, **When** the system attempts to fetch the resource, **Then** the system displays a timeout error message and allows the user to retry or cancel
3. **Given** the user enters a URL that returns a non-200 HTTP status, **When** the system attempts to fetch the resource, **Then** the system displays an appropriate error message (e.g., "Page not found" for 404) and allows the user to retry or cancel
4. **Given** the feeds.yaml file is corrupted or cannot be written, **When** the system attempts to save a new feed, **Then** the system displays an error message and attempts to recover the file, or creates a new one if recovery fails
5. **Given** any error occurs during feed addition, **When** the error is displayed, **Then** the user can return to the main menu without losing their place in the application

---

### Edge Cases

- What happens when the user provides a URL that redirects multiple times before reaching the final resource?
- How does the system handle URLs that require authentication or have access restrictions? → System skips authentication validation during feed addition, allows feed to be saved, authentication failures are handled during playback
- What happens when an HTML page contains multiple video players but only some are live streams?
- How does the system handle very large HTML pages that take a long time to parse?
- What happens when the user cancels the feed addition process mid-way?
- How does the system handle duplicate feed names when saving? → System automatically appends number suffix (e.g., "Name (2)")
- What happens when the feeds.yaml file is locked by another process?
- How does the system handle URLs with special characters or internationalized domain names?
- What happens when a direct stream URL is valid but the stream is currently offline?
- How does the system handle HTML pages that load content dynamically via JavaScript (client-side rendering)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an "Add Cam" option in the TUI main menu
- **FR-002**: System MUST prompt users to enter a cam name when adding a new feed
- **FR-003**: System MUST prompt users to enter a URL when adding a new feed
- **FR-004**: System MUST detect whether a provided URL is a direct stream URL (m3u8, mp4, webm, rtsp, etc.) or an HTML webpage
- **FR-005**: System MUST fetch and parse HTML content when a webpage URL is provided
- **FR-006**: System MUST extract embedded video stream URLs from HTML pages by identifying video tags, m3u8 links, and embedded player URLs
- **FR-007**: System MUST automatically select and save a feed when exactly one playable stream is found
- **FR-008**: System MUST present a selection list to users when multiple playable streams are found in an HTML page, displaying the user-provided feed name for each stream option
- **FR-009**: System MUST allow users to select a specific stream from a list of multiple options, where each option displays the user-provided feed name
- **FR-010**: System MUST save newly added feeds to the feeds.yaml configuration file
- **FR-011**: System MUST persist feed entries with name and url fields, and optionally window_size if specified
- **FR-012**: System MUST display clear, user-friendly error messages when feed addition fails
- **FR-013**: System MUST handle network connectivity errors gracefully with retry options
- **FR-014**: System MUST validate that provided URLs are accessible immediately after URL entry, before proceeding with stream detection or HTML parsing (authentication requirements are not validated during feed addition)
- **FR-015**: System MUST handle corrupted or invalid feeds.yaml files by attempting recovery or creating a new file
- **FR-016**: System MUST allow users to cancel the feed addition process at any point
- **FR-017**: System MUST update the saved feeds list immediately after successfully adding a new feed
- **FR-018**: System MUST automatically append a number suffix to duplicate feed names (e.g., "Panda Cam (2)", "Panda Cam (3)") when saving a new feed with an existing name
- **FR-019**: System MUST handle timeout scenarios when fetching web pages or validating stream URLs
- **FR-020**: System MUST provide appropriate error messages for different failure scenarios (network errors, invalid URLs, inaccessible pages, parsing failures)

### Key Entities *(include if feature involves data)*

- **Cam Feed**: Represents a single live camera feed entry. Contains a name (user-provided identifier), a url (direct stream URL or extracted stream URL), and optionally window_size (preferred display dimensions). Must be persistable to feeds.yaml and retrievable for display in the saved feeds list.

- **Feeds Configuration File**: Represents the persisted collection of all saved cam feeds. Stored as feeds.yaml in a standard location. Must support atomic writes to prevent corruption, validation on load, and graceful recovery from invalid or corrupted states. Contains a list of feed entries that can be added to, modified, or removed.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can successfully add a direct stream feed in under 30 seconds from selecting "Add Cam" to seeing the feed in their saved list
- **SC-002**: 95% of valid direct stream URLs are correctly detected and saved on first attempt
- **SC-003**: Users can successfully add a feed from an HTML page containing embedded streams in under 60 seconds
- **SC-004**: System successfully extracts playable streams from 90% of HTML pages that contain embedded video players
- **SC-005**: When multiple streams are found, 100% of users can successfully select their preferred stream from the list
- **SC-006**: All error scenarios display clear, actionable error messages that 100% of users can understand
- **SC-007**: System successfully recovers from network errors 100% of the time, allowing users to retry without losing their progress
- **SC-008**: Newly added feeds persist across application restarts 100% of the time
- **SC-009**: Feed addition process handles invalid or inaccessible URLs gracefully without crashing 100% of the time
- **SC-010**: Users can cancel the feed addition process at any point and return to the main menu without errors

## Assumptions

- Users have internet connectivity when adding feeds (though errors are handled gracefully when connectivity is unavailable)
- Users are familiar with URLs and can provide valid URL formats
- HTML pages containing embedded streams use standard HTML video tags or common embedded player patterns
- The feeds.yaml file is stored in a location accessible for reading and writing
- URLs may require authentication, but authentication validation is deferred to playback time; feed addition proceeds without authentication checks
- Network timeouts occur within a reasonable timeframe (e.g., 10-30 seconds) for user experience
- HTML pages are reasonably sized and can be parsed efficiently
- Users understand basic error messages and can take appropriate action (retry, cancel, try different URL)
- The system has sufficient memory and processing resources to parse HTML pages and extract stream URLs
- Feed names are user-provided identifiers; duplicate names are automatically resolved by appending number suffixes
