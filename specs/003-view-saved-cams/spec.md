# Feature Specification: View Saved Cam Feeds in TUI

**Feature Branch**: `003-view-saved-cams`
**Created**: 2024-12-19
**Status**: Draft
**Input**: User description: "look at the files in the plan directory. we are working on Story 3 — View Saved Cam Feeds in TUI @s3-specify.md"

## Clarifications

### Session 2024-12-19

- Q: How should duplicate feed names be displayed? → A: Display all duplicates with visual distinction (e.g., "Panda Cam", "Panda Cam (2)")
- Q: How should very long feed names be displayed? → A: Truncate long names with ellipsis (e.g., "Very Long Feed Na...")
- Q: How should feeds with valid names but invalid or missing URLs be handled? → A: Skip feeds with invalid or missing URLs silently (don't display them)
- Q: What should happen if the configuration file is modified by another process while viewing the feeds list? → A: Continue showing original list, refresh only when user returns to main menu and re-enters
- Q: How should the feeds list respond when the terminal is resized while viewing? → A: Automatically adjust layout and re-render list to fit new terminal size

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View and Navigate Saved Cam Feeds List (Priority: P1)

As a user, I want to see a clean list of all saved cams so I can select which one to watch.

**Why this priority**: This feature enables users to browse and access their saved camera feeds, which is essential for the core user workflow. Without this capability, users cannot easily discover or select feeds they've previously added. This delivers immediate value by providing a centralized view of all available feeds in an organized, navigable format.

**Independent Test**: Can be fully tested by loading saved feeds from the YAML configuration file and displaying them in a scrollable, selectable list. This delivers immediate value by enabling users to browse and select from their saved feeds.

**Acceptance Scenarios**:

1. **Given** the user is in the TUI main menu, **When** the user selects "View Saved Cams", **Then** the system displays a scrollable list showing all saved cam feeds with their names and emoji icons
2. **Given** the saved feeds list is displayed, **When** the user presses arrow keys or WASD keys, **Then** the system highlights different feed entries as the user navigates
3. **Given** a feed entry is highlighted, **When** the user confirms the selection (Enter key), **Then** the system transitions to the watch action for that selected feed
4. **Given** the saved feeds list contains multiple entries, **When** the list is displayed, **Then** all feeds are sorted alphabetically by name
5. **Given** the saved feeds list is longer than the terminal height, **When** the user navigates beyond the visible area, **Then** the list scrolls to keep the selected item visible
6. **Given** no feeds are saved in the configuration file, **When** the user selects "View Saved Cams", **Then** the system displays a clear message "No feeds saved" instead of an empty list
7. **Given** the configuration file contains malformed or invalid feed entries, **When** the user selects "View Saved Cams", **Then** the system displays only valid feeds and handles invalid entries gracefully without crashing

---

### User Story 2 - Handle Empty and Error States (Priority: P2)

As a user, I want clear feedback when no feeds are available or when there are issues loading feeds so I understand the current state of my saved feeds.

**Why this priority**: Proper handling of edge cases ensures a robust user experience and prevents confusion when feeds cannot be displayed. While not the primary feature, error handling is essential for user satisfaction and system reliability.

**Independent Test**: Can be fully tested by simulating empty configuration files, corrupted YAML, and invalid feed entries, verifying appropriate messages are displayed. This delivers value by providing a predictable, informative experience even when things go wrong.

**Acceptance Scenarios**:

1. **Given** no feeds are saved in the configuration file, **When** the user selects "View Saved Cams", **Then** the system displays a user-friendly message "No feeds saved" with guidance on how to add feeds
2. **Given** the configuration file is corrupted or invalid, **When** the user selects "View Saved Cams", **Then** the system attempts to recover valid feeds, displays a warning if recovery was needed, and shows only valid feeds
3. **Given** some feed entries in the configuration file are malformed, **When** the user selects "View Saved Cams", **Then** the system skips invalid entries, displays only valid feeds, and continues to function normally
4. **Given** the configuration file cannot be read (permissions, locked, etc.), **When** the user selects "View Saved Cams", **Then** the system displays an appropriate error message and allows the user to return to the main menu
5. **Given** any error occurs while loading feeds, **When** the error is displayed, **Then** the user can return to the main menu without losing their place in the application

---

### Edge Cases

- What happens when the user presses navigation keys very rapidly?
- How does the system handle feeds with very long names that exceed the terminal width? → Long names are truncated with ellipsis (e.g., "Very Long Feed Na...")
- What happens when the terminal is resized while viewing the feeds list? → Layout automatically adjusts and list re-renders to fit the new terminal size
- How does the system handle duplicate feed names in the configuration file? → All duplicates are displayed with visual distinction (e.g., "Panda Cam", "Panda Cam (2)")
- What happens when a feed entry has a valid name but an invalid or missing URL? → Feeds with invalid or missing URLs are skipped silently and not displayed in the list
- How does the system handle feeds with special characters or emoji in their names?
- What happens when the user tries to navigate an empty list (should not be possible if empty state is handled)?
- How does the system handle terminal size smaller than the minimum required for displaying the list?
- What happens when the configuration file is modified by another process while the feeds list is displayed? → Continue showing the originally loaded list, refresh only when user returns to main menu and re-enters the feeds list

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a "View Saved Cams" option in the TUI main menu
- **FR-002**: System MUST load all saved cam feeds from the YAML configuration file when "View Saved Cams" is selected
- **FR-003**: System MUST display saved feeds in a scrollable list format
- **FR-004**: System MUST display each feed with its name and a small emoji icon
- **FR-005**: System MUST sort all feeds alphabetically by name when displaying the list
- **FR-006**: System MUST allow users to navigate the feeds list using arrow keys, with WASD keys (W=up, S=down, A=left, D=right) as fallback when arrow keys are unavailable
- **FR-007**: System MUST highlight the currently selected feed entry as the user navigates
- **FR-008**: System MUST allow users to select a feed by confirming the selection (Enter key)
- **FR-009**: System MUST transition to the watch action when a feed is selected
- **FR-010**: System MUST display a clear message "No feeds saved" when the configuration file contains no valid feeds
- **FR-011**: System MUST handle empty configuration files gracefully without crashing
- **FR-012**: System MUST handle corrupted or invalid YAML configuration files gracefully
- **FR-013**: System MUST skip invalid or malformed feed entries and display only valid feeds
- **FR-013a**: System MUST skip feeds with invalid or missing URLs and not display them in the list
- **FR-014**: System MUST attempt to recover valid feeds from corrupted configuration files
- **FR-015**: System MUST display a warning message when configuration file recovery is needed
- **FR-016**: System MUST scroll the list to keep the selected item visible when navigating beyond the visible area
- **FR-017**: System MUST handle configuration file read errors (permissions, locked files, etc.) gracefully with appropriate error messages
- **FR-018**: System MUST allow users to return to the main menu from the feeds list at any time
- **FR-019**: System MUST display feeds list without requiring any write operations to the configuration file
- **FR-020**: System MUST continue to function normally even when some feed entries are invalid or malformed (including feeds with invalid or missing URLs)
- **FR-021**: System MUST display all feed entries with duplicate names, adding visual distinction (e.g., number suffix) to distinguish duplicates
- **FR-022**: System MUST truncate feed names that exceed the terminal width with ellipsis to maintain list readability
- **FR-023**: System MUST display the feeds list as loaded at entry time, and refresh the list only when the user returns to the main menu and re-enters the feeds list (not during active viewing)
- **FR-024**: System MUST automatically adjust layout and re-render the feeds list when the terminal is resized while viewing

### Key Entities *(include if feature involves data)*

- **Cam Feed**: Represents a single camera feed entry loaded from the configuration file. Contains a name (user-provided identifier), a url (direct stream URL), and optionally window_size (preferred display dimensions). Must be readable from feeds.yaml and displayable in the feeds list. Invalid or malformed entries are skipped during loading.

- **Feeds Configuration File**: Represents the persisted collection of all saved cam feeds. Stored as feeds.yaml in a standard location. Must support reading and validation on load, with graceful recovery from invalid or corrupted states. Contains a list of feed entries that can be empty, valid, or partially corrupted.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view their saved feeds list within 1 second of selecting "View Saved Cams"
- **SC-002**: 100% of valid saved feeds are displayed correctly in the list
- **SC-003**: Users can navigate through the feeds list using arrow keys or WASD keys without encountering any navigation errors
- **SC-004**: 100% of users can successfully select a feed from the list and transition to the watch action
- **SC-005**: System successfully handles empty configuration files 100% of the time, displaying appropriate messages without crashing
- **SC-006**: System successfully recovers and displays valid feeds from corrupted configuration files 100% of the time
- **SC-007**: Invalid or malformed feed entries are skipped 100% of the time without causing crashes or errors
- **SC-008**: Feeds list displays feeds sorted alphabetically by name 100% of the time
- **SC-009**: List scrolling keeps the selected item visible 100% of the time when navigating beyond visible area
- **SC-010**: Users can return to the main menu from the feeds list without errors 100% of the time

## Assumptions

- Users have saved at least one feed before accessing "View Saved Cams" (though empty state is handled gracefully)
- The configuration file (feeds.yaml) exists and is readable, though it may be empty or corrupted
- Feed names may be duplicated in the configuration file, and all duplicates are displayed with visual distinction (e.g., "Panda Cam", "Panda Cam (2)") to help users differentiate them
- Users are familiar with basic terminal navigation concepts (arrow keys, Enter key, navigation)
- The terminal window is ideally at least 80 columns wide and 24 rows tall for optimal display, but the TUI adapts to smaller sizes
- Configuration file corruption is rare but must be handled gracefully when it occurs
- Feed entries may have varying name lengths, and the display must accommodate reasonable name lengths
- The feeds list is read-only in this feature; no modifications to feeds are made when viewing

