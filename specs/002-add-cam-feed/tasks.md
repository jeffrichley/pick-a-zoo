# Tasks: Add a New Live Cam Feed

**Input**: Design documents from `/specs/002-add-cam-feed/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED per Constitution Principle I (Test-First Development - NON-NEGOTIABLE). All tests must be written and verified to FAIL before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths use `src/pick_a_zoo/` structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify project structure and dependencies

- [X] T001 [P] Verify project directory structure exists: `src/pick_a_zoo/core/`, `src/pick_a_zoo/tui/screens/`, `tests/unit/`, `tests/integration/`
- [X] T002 [P] Verify all dependencies from pyproject.toml are installed (httpx, beautifulsoup4, lxml, m3u8, textual, rich, PyYAML, pydantic, platformdirs, loguru)
- [X] T003 [P] Verify pytest configuration in pyproject.toml (testpaths, markers)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Feed Discovery Library (Constitution: Library-First)

- [X] T004 Create `src/pick_a_zoo/core/feed_discovery.py` module with module docstring
- [X] T005 [P] [US1] Create URLType enum in `src/pick_a_zoo/core/feed_discovery.py` with DIRECT_STREAM and HTML_PAGE values
- [X] T006 [P] [US1] Create StreamCandidate dataclass in `src/pick_a_zoo/core/feed_discovery.py` (url: str, source_type: str)
- [X] T007 [P] [US1] Create URLValidationResult dataclass in `src/pick_a_zoo/core/feed_discovery.py` (is_accessible: bool, status_code: int | None, error_message: str | None, content_type: str | None)
- [X] T008 [P] [US1] Create FeedDiscoveryError exception class in `src/pick_a_zoo/core/feed_discovery.py` with user-friendly message support
- [X] T009 [P] [US1] Create HTMLParseError exception class in `src/pick_a_zoo/core/feed_discovery.py` inheriting from FeedDiscoveryError
- [X] T010 [P] [US1] Create URLValidationError exception class in `src/pick_a_zoo/core/feed_discovery.py` inheriting from FeedDiscoveryError
- [X] T011 [US1] Implement `detect_url_type(url: str) -> URLType` function in `src/pick_a_zoo/core/feed_discovery.py` with pattern matching for direct streams
- [X] T012 [US1] Add HTTP HEAD request fallback to `detect_url_type()` in `src/pick_a_zoo/core/feed_discovery.py` for Content-Type checking
- [X] T013 [US1] Add redirect handling (up to 5 redirects) to `detect_url_type()` in `src/pick_a_zoo/core/feed_discovery.py`
- [X] T014 [US2] Implement `extract_streams_from_html(html_content: str, base_url: str) -> list[StreamCandidate]` function in `src/pick_a_zoo/core/feed_discovery.py` with BeautifulSoup4 parsing
- [X] T015 [US2] Add extraction from `<video>` tags in `extract_streams_from_html()` in `src/pick_a_zoo/core/feed_discovery.py`
- [X] T016 [US2] Add extraction from `<source>` tags in `extract_streams_from_html()` in `src/pick_a_zoo/core/feed_discovery.py`
- [X] T017 [US2] Add m3u8 link search in page content in `extract_streams_from_html()` in `src/pick_a_zoo/core/feed_discovery.py`
- [X] T018 [US2] Add basic iframe extraction (common video player domains) in `extract_streams_from_html()` in `src/pick_a_zoo/core/feed_discovery.py`
- [X] T019 [US2] Add relative URL resolution to absolute URLs in `extract_streams_from_html()` in `src/pick_a_zoo/core/feed_discovery.py`
- [X] T020 [US2] Add stream URL deduplication in `extract_streams_from_html()` in `src/pick_a_zoo/core/feed_discovery.py`
- [X] T021 [US1] Implement `validate_url_accessibility(url: str, timeout: float = 15.0) -> URLValidationResult` function in `src/pick_a_zoo/core/feed_discovery.py` with httpx HTTP HEAD request
- [X] T022 [US1] Add redirect handling (up to 5 redirects) to `validate_url_accessibility()` in `src/pick_a_zoo/core/feed_discovery.py`
- [X] T023 [US1] Add HTTP status code checking (200-299 = accessible) to `validate_url_accessibility()` in `src/pick_a_zoo/core/feed_discovery.py`
- [X] T024 [US1] Add network error handling (timeout, connection refused, DNS failure) to `validate_url_accessibility()` in `src/pick_a_zoo/core/feed_discovery.py`
- [X] T025 [P] [US1] Add structured logging (loguru) to all feed_discovery functions in `src/pick_a_zoo/core/feed_discovery.py`

### Feed Manager Extension

- [X] T026 [US1] Implement `resolve_duplicate_name(name: str, existing_feeds: list[Feed]) -> str` function in `src/pick_a_zoo/core/feed_manager.py` with auto-append number suffix logic
- [X] T027 [US1] Add unique name checking logic to `resolve_duplicate_name()` in `src/pick_a_zoo/core/feed_manager.py`
- [X] T028 [US1] Add number suffix increment logic to `resolve_duplicate_name()` in `src/pick_a_zoo/core/feed_manager.py` (handles "Name (2)", "Name (3)", etc.)

**Checkpoint**: Foundation ready - feed_discovery library is functional and independently testable, duplicate name resolution is available. User story implementation can now begin.

---

## Phase 3: User Story 1 - Add Direct Stream Feed (Priority: P1) 🎯 MVP

**Goal**: Enable users to add a new cam feed by providing a name and a direct stream URL so that they can watch live animal cameras from any publicly available stream source.

**Independent Test**: Provide a direct stream URL, verify the feed is saved and appears in the saved feeds list. Test with various stream formats (m3u8, mp4, webm, rtsp). Verify URL validation, duplicate name handling, and error scenarios.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

#### Unit Tests - Feed Discovery

- [X] T029 [P] [US1] Create unit test file `tests/unit/test_feed_discovery.py` with test for `detect_url_type()` with direct stream URL (.m3u8)
- [X] T030 [P] [US1] Add test for `detect_url_type()` with direct stream URL (.mp4) in `tests/unit/test_feed_discovery.py`
- [X] T031 [P] [US1] Add test for `detect_url_type()` with direct stream URL (.webm) in `tests/unit/test_feed_discovery.py`
- [X] T032 [P] [US1] Add test for `detect_url_type()` with direct stream URL (rtsp://) in `tests/unit/test_feed_discovery.py`
- [X] T033 [P] [US1] Add test for `detect_url_type()` with HTML page URL (via Content-Type) in `tests/unit/test_feed_discovery.py`
- [X] T034 [P] [US1] Add test for `detect_url_type()` with redirect handling in `tests/unit/test_feed_discovery.py`
- [X] T035 [P] [US1] Add test for `detect_url_type()` error handling (network error) in `tests/unit/test_feed_discovery.py`
- [X] T036 [P] [US1] Add test for `validate_url_accessibility()` with accessible URL in `tests/unit/test_feed_discovery.py`
- [X] T037 [P] [US1] Add test for `validate_url_accessibility()` with inaccessible URL (404) in `tests/unit/test_feed_discovery.py`
- [X] T038 [P] [US1] Add test for `validate_url_accessibility()` with timeout scenario in `tests/unit/test_feed_discovery.py`
- [X] T039 [P] [US1] Add test for `validate_url_accessibility()` with network error in `tests/unit/test_feed_discovery.py`
- [X] T040 [P] [US1] Add test for `validate_url_accessibility()` with redirect handling in `tests/unit/test_feed_discovery.py`

#### Unit Tests - Feed Manager Extension

- [X] T041 [P] [US1] Add test for `resolve_duplicate_name()` with unique name in `tests/unit/test_feed_manager.py`
- [X] T042 [P] [US1] Add test for `resolve_duplicate_name()` with single duplicate (appends " (2)") in `tests/unit/test_feed_manager.py`
- [X] T043 [P] [US1] Add test for `resolve_duplicate_name()` with multiple duplicates (increments number) in `tests/unit/test_feed_manager.py`
- [X] T044 [P] [US1] Add test for `resolve_duplicate_name()` edge case (name with existing number suffix) in `tests/unit/test_feed_manager.py`

#### Unit Tests - Add Feed Screen

- [X] T045 [P] [US1] Create unit test file `tests/unit/test_add_feed.py` with test for AddFeedScreen name input validation
- [X] T046 [P] [US1] Add test for AddFeedScreen URL input validation in `tests/unit/test_add_feed.py`
- [X] T047 [P] [US1] Add test for AddFeedScreen direct stream workflow (success case) in `tests/unit/test_add_feed.py`
- [X] T048 [P] [US1] Add test for AddFeedScreen invalid URL error handling in `tests/unit/test_add_feed.py`
- [X] T049 [P] [US1] Add test for AddFeedScreen inaccessible URL error handling in `tests/unit/test_add_feed.py`
- [X] T050 [P] [US1] Add test for AddFeedScreen cancellation at name entry in `tests/unit/test_add_feed.py`
- [X] T051 [P] [US1] Add test for AddFeedScreen cancellation at URL entry in `tests/unit/test_add_feed.py`

#### Integration Tests

- [X] T052 [P] [US1] Create integration test file `tests/integration/test_feed_discovery_integration.py` with test for end-to-end direct stream feed addition
- [X] T053 [P] [US1] Add test for duplicate name resolution integration in `tests/integration/test_feed_discovery_integration.py`
- [X] T054 [P] [US1] Add test for URL validation integration in `tests/integration/test_feed_discovery_integration.py`

### Implementation for User Story 1

#### Add Feed Screen

- [X] T055 [US1] Create `src/pick_a_zoo/tui/screens/add_feed.py` module with AddFeedScreen class inheriting from textual.screen.Screen
- [X] T056 [US1] Implement `on_mount()` method in AddFeedScreen in `src/pick_a_zoo/tui/screens/add_feed.py` to initialize screen state and display name prompt
- [X] T057 [US1] Implement `on_input_submitted(name: str)` method in AddFeedScreen in `src/pick_a_zoo/tui/screens/add_feed.py` to handle name input and validate
- [X] T058 [US1] Implement `on_url_submitted(url: str)` method in AddFeedScreen in `src/pick_a_zoo/tui/screens/add_feed.py` to handle URL input
- [X] T059 [US1] Add URL type detection call to `on_url_submitted()` in `src/pick_a_zoo/tui/screens/add_feed.py` using `detect_url_type()`
- [X] T060 [US1] Add URL validation call to `on_url_submitted()` in `src/pick_a_zoo/tui/screens/add_feed.py` using `validate_url_accessibility()` for direct streams
- [X] T061 [US1] Add Feed creation and duplicate name resolution to `on_url_submitted()` in `src/pick_a_zoo/tui/screens/add_feed.py`
- [X] T062 [US1] Add feed saving logic to `on_url_submitted()` in `src/pick_a_zoo/tui/screens/add_feed.py` using `save_feeds()`
- [X] T063 [US1] Add error message display for invalid URLs in AddFeedScreen in `src/pick_a_zoo/tui/screens/add_feed.py`
- [X] T064 [US1] Add error message display for inaccessible URLs in AddFeedScreen in `src/pick_a_zoo/tui/screens/add_feed.py`
- [X] T065 [US1] Add retry option for error scenarios in AddFeedScreen in `src/pick_a_zoo/tui/screens/add_feed.py`
- [X] T066 [US1] Implement `on_cancel()` method in AddFeedScreen in `src/pick_a_zoo/tui/screens/add_feed.py` to return to main menu
- [X] T067 [US1] Add keyboard bindings (Escape, 'q') for cancellation in AddFeedScreen in `src/pick_a_zoo/tui/screens/add_feed.py`

#### Main Menu Integration

- [X] T068 [US1] Add "Add Cam" menu option to MainMenuScreen in `src/pick_a_zoo/tui/screens/main_menu.py`
- [X] T069 [US1] Implement `on_add_cam_selected()` method in MainMenuScreen in `src/pick_a_zoo/tui/screens/main_menu.py` to navigate to AddFeedScreen
- [X] T070 [US1] Add keyboard binding for "Add Cam" option in MainMenuScreen in `src/pick_a_zoo/tui/screens/main_menu.py`

**Checkpoint**: User Story 1 complete - Users can add direct stream feeds. MVP functionality delivered.

---

## Phase 4: User Story 2 - Add Feed from HTML Page (Priority: P2)

**Goal**: Enable users to add a cam feed by providing a webpage URL so that the system can automatically discover and extract embedded video streams from HTML pages.

**Independent Test**: Provide an HTML page URL containing embedded video players, verify the system extracts and saves the stream. Test with single stream (auto-select), multiple streams (user selection), and no streams (error message).

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

#### Unit Tests - HTML Extraction

- [ ] T071 [P] [US2] Add test for `extract_streams_from_html()` with single `<video>` tag in `tests/unit/test_feed_discovery.py`
- [ ] T072 [P] [US2] Add test for `extract_streams_from_html()` with multiple `<video>` tags in `tests/unit/test_feed_discovery.py`
- [ ] T073 [P] [US2] Add test for `extract_streams_from_html()` with `<source>` tags in `tests/unit/test_feed_discovery.py`
- [ ] T074 [P] [US2] Add test for `extract_streams_from_html()` with m3u8 links in page content in `tests/unit/test_feed_discovery.py`
- [ ] T075 [P] [US2] Add test for `extract_streams_from_html()` with relative URLs (resolution to absolute) in `tests/unit/test_feed_discovery.py`
- [ ] T076 [P] [US2] Add test for `extract_streams_from_html()` with duplicate URLs (deduplication) in `tests/unit/test_feed_discovery.py`
- [ ] T077 [P] [US2] Add test for `extract_streams_from_html()` with malformed HTML in `tests/unit/test_feed_discovery.py`
- [ ] T078 [P] [US2] Add test for `extract_streams_from_html()` with no streams found in `tests/unit/test_feed_discovery.py`

#### Unit Tests - Add Feed Screen (HTML Page)

- [ ] T079 [P] [US2] Add test for AddFeedScreen HTML page detection in `tests/unit/test_add_feed.py`
- [ ] T080 [P] [US2] Add test for AddFeedScreen HTML fetching in `tests/unit/test_add_feed.py`
- [ ] T081 [P] [US2] Add test for AddFeedScreen single stream auto-selection in `tests/unit/test_add_feed.py`
- [ ] T082 [P] [US2] Add test for AddFeedScreen multiple streams list display in `tests/unit/test_add_feed.py`
- [ ] T083 [P] [US2] Add test for AddFeedScreen stream selection from list in `tests/unit/test_add_feed.py`
- [ ] T084 [P] [US2] Add test for AddFeedScreen no streams found error in `tests/unit/test_add_feed.py`

#### Integration Tests

- [ ] T085 [P] [US2] Add test for end-to-end HTML page feed addition (single stream) in `tests/integration/test_feed_discovery_integration.py`
- [ ] T086 [P] [US2] Add test for end-to-end HTML page feed addition (multiple streams) in `tests/integration/test_feed_discovery_integration.py`

### Implementation for User Story 2

#### HTML Fetching and Parsing

- [ ] T087 [US2] Add HTML content fetching to `on_url_submitted()` in AddFeedScreen in `src/pick_a_zoo/tui/screens/add_feed.py` using httpx when URL type is HTML_PAGE
- [ ] T088 [US2] Add HTML parsing and stream extraction call to `on_url_submitted()` in `src/pick_a_zoo/tui/screens/add_feed.py` using `extract_streams_from_html()`
- [ ] T089 [US2] Add single stream auto-selection logic to `on_url_submitted()` in `src/pick_a_zoo/tui/screens/add_feed.py` when exactly one stream found
- [ ] T090 [US2] Add multiple streams list display to AddFeedScreen in `src/pick_a_zoo/tui/screens/add_feed.py` using Textual ListView widget
- [ ] T091 [US2] Implement `on_stream_selected(stream_index: int)` method in AddFeedScreen in `src/pick_a_zoo/tui/screens/add_feed.py` to handle user stream selection
- [ ] T092 [US2] Add stream selection confirmation logic to `on_stream_selected()` in `src/pick_a_zoo/tui/screens/add_feed.py`
- [ ] T093 [US2] Add Feed creation and saving logic to `on_stream_selected()` in `src/pick_a_zoo/tui/screens/add_feed.py`
- [ ] T094 [US2] Add "no streams found" error message display to AddFeedScreen in `src/pick_a_zoo/tui/screens/add_feed.py`
- [ ] T095 [US2] Add keyboard navigation (arrow keys) for stream list in AddFeedScreen in `src/pick_a_zoo/tui/screens/add_feed.py`
- [ ] T096 [US2] Add Enter key binding for stream selection confirmation in AddFeedScreen in `src/pick_a_zoo/tui/screens/add_feed.py`

**Checkpoint**: User Story 2 complete - Users can add feeds from HTML pages with automatic stream extraction.

---

## Phase 5: User Story 3 - Handle Network and Validation Errors (Priority: P3)

**Goal**: Provide clear error messages when adding feeds fails so that users understand what went wrong and can take appropriate action.

**Independent Test**: Simulate various error conditions (network failures, invalid URLs, inaccessible pages) and verify appropriate error messages are displayed. Test retry functionality and cancellation at error points.

**Note**: Most error handling is integrated into US1 and US2. This phase focuses on comprehensive error scenarios and user experience polish.

### Tests for User Story 3 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

#### Unit Tests - Error Handling

- [ ] T097 [P] [US3] Add test for network connectivity error handling in `tests/unit/test_feed_discovery.py`
- [ ] T098 [P] [US3] Add test for timeout error handling in `tests/unit/test_feed_discovery.py`
- [ ] T099 [P] [US3] Add test for non-200 HTTP status error handling (404, 500, etc.) in `tests/unit/test_feed_discovery.py`
- [ ] T100 [P] [US3] Add test for corrupted feeds.yaml file error handling in `tests/unit/test_feed_manager.py`
- [ ] T101 [P] [US3] Add test for file write permission error handling in `tests/unit/test_feed_manager.py`
- [ ] T102 [P] [US3] Add test for error message user-friendliness in `tests/unit/test_add_feed.py`
- [ ] T103 [P] [US3] Add test for retry option functionality in `tests/unit/test_add_feed.py`
- [ ] T104 [P] [US3] Add test for cancellation at error point in `tests/unit/test_add_feed.py`

#### Integration Tests

- [ ] T105 [P] [US3] Add test for network error recovery flow in `tests/integration/test_feed_discovery_integration.py`
- [ ] T106 [P] [US3] Add test for corrupted file recovery flow in `tests/integration/test_feed_discovery_integration.py`

### Implementation for User Story 3

#### Enhanced Error Handling

- [ ] T107 [US3] Enhance error messages in feed_discovery exceptions in `src/pick_a_zoo/core/feed_discovery.py` with user-friendly descriptions
- [ ] T108 [US3] Add specific error messages for network connectivity issues in `src/pick_a_zoo/core/feed_discovery.py`
- [ ] T109 [US3] Add specific error messages for timeout scenarios in `src/pick_a_zoo/core/feed_discovery.py`
- [ ] T110 [US3] Add specific error messages for HTTP status codes (404, 500, etc.) in `src/pick_a_zoo/core/feed_discovery.py`
- [ ] T111 [US3] Enhance error display in AddFeedScreen in `src/pick_a_zoo/tui/screens/add_feed.py` with actionable messages
- [ ] T112 [US3] Add retry button/widget to AddFeedScreen error display in `src/pick_a_zoo/tui/screens/add_feed.py`
- [ ] T113 [US3] Implement retry logic in AddFeedScreen in `src/pick_a_zoo/tui/screens/add_feed.py` to re-attempt failed operations
- [ ] T114 [US3] Add error context preservation in AddFeedScreen in `src/pick_a_zoo/tui/screens/add_feed.py` to allow retry without losing entered data
- [ ] T115 [US3] Enhance corrupted file error handling in `save_feeds()` in `src/pick_a_zoo/core/feed_manager.py` with recovery attempt
- [ ] T116 [US3] Add file lock detection and error handling in `save_feeds()` in `src/pick_a_zoo/core/feed_manager.py`

**Checkpoint**: User Story 3 complete - Comprehensive error handling with user-friendly messages and retry options.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final polish, edge cases, and integration verification

### Edge Cases

- [ ] T117 [P] Add handling for URLs with multiple redirects (beyond 5) in `src/pick_a_zoo/core/feed_discovery.py`
- [ ] T118 [P] Add handling for URLs with special characters/IDN in `src/pick_a_zoo/core/feed_discovery.py`
- [ ] T119 [P] Add handling for very large HTML pages (timeout/performance) in `src/pick_a_zoo/core/feed_discovery.py`
- [ ] T120 [P] Add handling for HTML pages with JavaScript-rendered content (basic detection, error message) in `src/pick_a_zoo/core/feed_discovery.py`
- [ ] T121 [P] Add handling for valid URL but offline stream in `src/pick_a_zoo/core/feed_discovery.py` (validation passes, playback fails later)

### Integration & Verification

- [ ] T122 [P] Verify all user stories work together end-to-end
- [ ] T123 [P] Verify feed addition updates main menu feed list immediately
- [ ] T124 [P] Verify feeds persist across application restarts
- [ ] T125 [P] Verify cancellation at any point returns to main menu without errors
- [ ] T126 [P] Run full test suite and verify all tests pass
- [ ] T127 [P] Verify performance goals (SC-001: <30s direct stream, SC-003: <60s HTML page)

### Documentation

- [ ] T128 [P] Update README.md with feed addition feature documentation
- [ ] T129 [P] Add docstrings to all new functions and classes
- [ ] T130 [P] Verify all contracts are implemented correctly

---

## Dependencies & Story Completion Order

### Story Dependencies

1. **Phase 2 (Foundational)** → Must complete before any user story
   - feed_discovery.py library
   - resolve_duplicate_name() function

2. **Phase 3 (US1 - Direct Stream)** → Can be completed independently
   - Depends on: Phase 2
   - MVP scope: This is the minimum viable product

3. **Phase 4 (US2 - HTML Page)** → Depends on US1
   - Depends on: Phase 2, Phase 3
   - Extends US1 functionality with HTML parsing

4. **Phase 5 (US3 - Error Handling)** → Integrated into US1/US2
   - Depends on: Phase 2, Phase 3, Phase 4
   - Enhances error handling across all workflows

5. **Phase 6 (Polish)** → Final phase
   - Depends on: All previous phases

### Parallel Execution Opportunities

**Within Phase 2**:
- T005-T010 can run in parallel (different exception/data classes)
- T014-T020 can run in parallel (different extraction methods)
- T021-T024 can run in parallel (different validation aspects)

**Within Phase 3**:
- T029-T044 can run in parallel (different test files)
- T055-T067 can run in parallel with tests (implementation vs tests)

**Within Phase 4**:
- T071-T078 can run in parallel (different test scenarios)
- T087-T096 can run in parallel with tests

## Implementation Strategy

### MVP First (Incremental Delivery)

**MVP Scope**: Phase 3 (User Story 1 - Add Direct Stream Feed)
- Enables core functionality: adding direct stream feeds
- Delivers immediate user value
- Independently testable and deployable

**Incremental Enhancements**:
1. **MVP**: Direct stream feeds (Phase 3)
2. **Enhancement 1**: HTML page support (Phase 4)
3. **Enhancement 2**: Comprehensive error handling (Phase 5)
4. **Enhancement 3**: Edge cases and polish (Phase 6)

### Test-First Approach

All implementation phases follow TDD:
1. Write tests (marked with ⚠️)
2. Verify tests FAIL
3. Implement functionality
4. Verify tests PASS
5. Refactor if needed

---

## Summary

- **Total Tasks**: 130
- **Tasks per User Story**:
  - Phase 2 (Foundational): 25 tasks
  - Phase 3 (US1 - Direct Stream): 42 tasks
  - Phase 4 (US2 - HTML Page): 26 tasks
  - Phase 5 (US3 - Error Handling): 20 tasks
  - Phase 6 (Polish): 17 tasks
- **Parallel Opportunities**: Multiple tasks can run in parallel within each phase
- **MVP Scope**: Phase 3 (User Story 1) - 42 tasks
- **Independent Test Criteria**: Each user story has clear test criteria defined above
