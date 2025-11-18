# Feature Specification: Launch Video Window for Selected Cam

**Feature Branch**: `004-launch-video-window`
**Created**: 2024-12-19
**Status**: Draft
**Input**: User description: "Story 4 — Launch Video Window for Selected Cam. Open a GUI window displaying the selected live stream while keeping the TUI open."

## Clarifications

### Session 2024-12-19

- Q: When a user opens a video window and then selects another feed, should the system open a new window or replace the existing one? → A: Open a new window for each feed (allow multiple simultaneous windows)
- Q: Should window dimensions be stored per individual feed or globally? → A: Per-feed window dimensions (each feed remembers its own size, as already stored in YAML structure)
- Q: When the user closes/quits the TUI while video windows are still open, what should happen to those video windows? → A: Close all video windows when TUI closes (single process, windows managed by TUI)
- Q: What are the minimum and maximum window dimensions that should be considered valid? → A: Minimum 320x240, maximum 7680x4320

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Launch Video Window and Play Stream (Priority: P1)

As a user, I want to select a saved cam feed and have it open in a separate window so I can watch the live video stream while keeping the TUI available for navigation.

**Why this priority**: This is the core "watch" experience that enables users to actually view their saved camera feeds. Without this functionality, users can save feeds but cannot watch them, making the entire application incomplete. This delivers immediate value by providing the primary use case for the application - watching live animal camera streams.

**Independent Test**: Can be fully tested by selecting a feed from the saved feeds list and verifying a video window opens and begins playing the stream automatically. This delivers immediate value by enabling users to watch their saved camera feeds.

**Acceptance Scenarios**:

1. **Given** the user has selected a feed from the saved feeds list, **When** the user confirms the selection, **Then** a separate video window opens displaying the live stream
2. **Given** a video window has opened, **When** the window appears, **Then** the video stream begins playing automatically without requiring additional user interaction
3. **Given** a video window is open, **When** the user interacts with the TUI, **Then** the TUI remains functional and accessible while the video window stays open
4. **Given** a video window is open, **When** the user closes the video window, **Then** the TUI remains open and functional, allowing the user to select another feed or navigate elsewhere
5. **Given** multiple feeds are available, **When** the user opens a video window for one feed and then selects another feed, **Then** the system opens a new video window for the newly selected feed, allowing multiple video windows to be open simultaneously

---

### User Story 2 - Resize Video Window and Persist Dimensions (Priority: P2)

As a user, I want to resize the video window to my preferred size and have those dimensions remembered for future sessions so I don't have to resize it every time.

**Why this priority**: Window resizing enhances user experience by allowing customization, and persisting dimensions provides convenience for repeated use. While not critical for initial functionality, this significantly improves usability and demonstrates proper state management. This delivers value by reducing repetitive actions and personalizing the viewing experience.

**Independent Test**: Can be fully tested by resizing a video window, closing it, and verifying that when a new window opens, it uses the previously saved dimensions. This delivers value by providing a personalized, consistent viewing experience.

**Acceptance Scenarios**:

1. **Given** a video window is open, **When** the user resizes the window by dragging its edges, **Then** the window resizes smoothly and the video content adjusts to fit the new dimensions
2. **Given** a video window has been resized, **When** the user closes the window, **Then** the new dimensions are saved to the configuration file
3. **Given** a video window has been resized and saved for a specific feed, **When** the user opens a video window for that same feed again, **Then** the window opens with the previously saved dimensions for that feed
4. **Given** no previous window dimensions have been saved, **When** a video window opens, **Then** the window uses sensible default dimensions that provide a good viewing experience
5. **Given** saved window dimensions are outside the valid range (less than 320x240 or greater than 7680x4320), **When** a video window opens, **Then** the system uses default dimensions instead of the invalid saved values

---

### User Story 3 - Handle Stream Errors Gracefully (Priority: P3)

As a user, I want clear feedback when a video stream cannot be played so I understand what went wrong and can take appropriate action.

**Why this priority**: Error handling ensures a robust user experience and prevents frustration when streams are unavailable. While not the primary feature, proper error handling is essential for user satisfaction and system reliability. This delivers value by providing a smooth, predictable experience even when things go wrong.

**Independent Test**: Can be fully tested by attempting to play an unavailable stream and verifying appropriate error messages are displayed in the video window. This delivers value by providing clear feedback and preventing user confusion.

**Acceptance Scenarios**:

1. **Given** a user selects a feed with an unavailable stream URL, **When** the video window attempts to play the stream, **Then** the window displays a user-friendly error message explaining that the stream is unavailable
2. **Given** a stream becomes unavailable during playback, **When** the connection is lost, **Then** the video window displays an error message indicating the connection was lost
3. **Given** a stream URL is invalid or malformed, **When** the video window attempts to play the stream, **Then** the window displays a clear error message and allows the user to close the window and return to the TUI
4. **Given** network connectivity is lost, **When** the video window attempts to play a stream, **Then** the window displays an appropriate network error message
5. **Given** any error occurs while attempting to play a stream, **When** the error is displayed, **Then** the user can close the error window and return to the TUI without losing their place in the application

---

### Edge Cases

- How does the system handle resource management when multiple video windows are open simultaneously?
- How does the system handle very slow network connections or buffering issues?
- What happens when a stream URL requires authentication that wasn't provided during feed addition?
- How does the system handle video streams with different aspect ratios when resizing?
- What happens when the saved window dimensions would place the window off-screen (e.g., user changed monitor setup)?
- How does the system handle video codecs that aren't supported by the system?
- All video windows are closed when the TUI exits (single process, windows managed together)
- How does the system handle streams that are temporarily unavailable but become available later?
- What happens when the configuration file is locked or cannot be written when saving window dimensions?
- How does the system handle extremely long feed URLs that might cause display issues?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST open a separate video window when a user selects a feed from the saved feeds list
- **FR-002**: System MUST begin playing the video stream automatically when the video window opens
- **FR-003**: System MUST keep the TUI open and functional while a video window is displayed
- **FR-004**: System MUST allow users to close the video window independently of the TUI
- **FR-004a**: System MUST support multiple video windows open simultaneously, with each window displaying a different feed
- **FR-004b**: System MUST close all video windows when the TUI is closed (single process, all windows managed together)
- **FR-005**: System MUST allow users to resize the video window by dragging its edges
- **FR-006**: System MUST save window dimensions to the configuration file for the specific feed when the window is resized and closed
- **FR-007**: System MUST load previously saved window dimensions for the specific feed when opening a video window for that feed
- **FR-008**: System MUST use sensible default window dimensions when no saved dimensions exist for a feed
- **FR-009**: System MUST validate saved window dimensions and use defaults if dimensions are outside the valid range (minimum 320x240, maximum 7680x4320)
- **FR-010**: System MUST display user-friendly error messages when a stream is unavailable or cannot be played
- **FR-011**: System MUST display error messages when network connectivity issues prevent stream playback
- **FR-012**: System MUST allow users to close error windows and return to the TUI
- **FR-013**: System MUST handle stream connection losses gracefully by displaying appropriate error messages
- **FR-014**: System MUST read the feed URL from the selected feed's configuration data
- **FR-015**: System MUST persist updated window dimensions to the configuration file
- **FR-016**: System MUST handle configuration file write errors gracefully without crashing the application

### Key Entities *(include if feature involves data)*

- **Feed**: Represents a saved camera feed with name, URL, and optional window size preferences stored per feed. The feed URL is used to load the video stream, and window size preferences are updated per feed when the user resizes the window for that specific feed.

- **Configuration File**: Represents the persisted state of saved cam feeds and window preferences. Contains feed entries with names, URLs, and window size preferences. Window size is updated when users resize video windows, and must be readable and writable with proper error handling.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can open a video window and begin watching a stream within 3 seconds of selecting a feed
- **SC-002**: 100% of successfully opened video windows begin playing automatically without requiring additional user interaction
- **SC-003**: Users can resize video windows smoothly without noticeable lag or stuttering
- **SC-004**: Window dimensions are persisted correctly 100% of the time when windows are resized and closed
- **SC-005**: Previously saved window dimensions are restored correctly 100% of the time when opening video windows for feeds that have saved dimensions
- **SC-006**: Error messages are displayed within 2 seconds when streams are unavailable or cannot be played
- **SC-007**: Users can successfully close error windows and return to the TUI 100% of the time without losing their place in the application
- **SC-008**: The TUI remains fully functional while video windows are open, allowing users to navigate and select other feeds without interruption

## Assumptions

- Users have a display capable of showing both the TUI and a separate video window simultaneously
- The system has appropriate video playback libraries and codecs installed to handle common stream formats (m3u8, mp4, webm, rtsp, etc.)
- Network connectivity is available for streaming video content (though errors are handled gracefully when it's not)
- Users understand basic window management concepts (resizing, closing windows)
- Video streams are publicly accessible or authentication was handled during feed addition
- The configuration file is writable and accessible for saving window dimensions
- Window dimensions are stored per-feed in the YAML configuration file structure (each feed entry can have its own window_size with width and height)
- Video windows are PyQt6 windows running in the same process as the TUI, managed by a shared QApplication instance and closed when TUI exits
