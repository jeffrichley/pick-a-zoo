# Tasks: View Saved Cam Feeds in TUI

**Input**: Design documents from `/specs/003-view-saved-cams/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are REQUIRED per Constitution Principle I (Test-First Development - NON-NEGOTIABLE). All tests must be written and verified to FAIL before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths use `src/pick_a_zoo/` structure per plan.md

---

## Phase 1: Setup (Verification)

**Purpose**: Verify existing infrastructure and prepare for new feature

- [X] T001 Verify existing `src/pick_a_zoo/core/feed_manager.py` has `load_feeds()` function
- [X] T002 Verify existing `src/pick_a_zoo/core/models.py` has Feed and WindowSize models
- [X] T003 Verify existing `src/pick_a_zoo/tui/screens/main_menu.py` has routing capability
- [X] T004 [P] Verify all dependencies from pyproject.toml are installed (textual, rich, PyYAML, pydantic, platformdirs, loguru)
- [X] T005 [P] Verify pytest configuration in pyproject.toml supports TUI testing

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core utilities needed before user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### URL Validation Utility

- [X] T006 [P] Create URL validation helper function `_is_valid_url(url: str) -> bool` in `src/pick_a_zoo/tui/screens/view_saved_cams.py` (checks for non-empty string and valid URL format)

**Checkpoint**: Foundation ready - URL validation utility exists. User story implementation can now begin.

---

## Phase 3: User Story 1 - View and Navigate Saved Cam Feeds List (Priority: P1) 🎯 MVP

**Goal**: Display all saved camera feeds in a scrollable, selectable TUI list. Users can navigate through feeds using arrow keys or WASD keys, view feeds sorted alphabetically by name, and select a feed to transition to the watch action.

**Independent Test**: Load saved feeds from YAML configuration file and display them in a scrollable, selectable list. Test navigation with arrow keys and WASD keys. Verify feeds are sorted alphabetically. Verify feed selection transitions to watch action (placeholder for Story 4).

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

#### Unit Tests

- [X] T007 [P] [US1] Create unit test file `tests/unit/test_view_saved_cams.py` with test for ViewSavedCamsScreen rendering with feeds
- [X] T008 [P] [US1] Add test for ViewSavedCamsScreen loading feeds from feed_manager in `tests/unit/test_view_saved_cams.py`
- [X] T009 [P] [US1] Add test for ViewSavedCamsScreen filtering invalid feeds (missing/invalid URLs) in `tests/unit/test_view_saved_cams.py`
- [X] T010 [P] [US1] Add test for ViewSavedCamsScreen sorting feeds alphabetically by name in `tests/unit/test_view_saved_cams.py`
- [X] T011 [P] [US1] Add test for ViewSavedCamsScreen resolving duplicate feed names with number suffix in `tests/unit/test_view_saved_cams.py`
- [X] T012 [P] [US1] Add test for ViewSavedCamsScreen truncating long feed names with ellipsis in `tests/unit/test_view_saved_cams.py`
- [X] T013 [P] [US1] Add test for ViewSavedCamsScreen displaying emoji icons with feed names in `tests/unit/test_view_saved_cams.py`
- [X] T014 [P] [US1] Add test for ViewSavedCamsScreen keyboard navigation (arrow keys) in `tests/unit/test_view_saved_cams.py`
- [X] T015 [P] [US1] Add test for ViewSavedCamsScreen WASD fallback navigation in `tests/unit/test_view_saved_cams.py`
- [X] T016 [P] [US1] Add test for ViewSavedCamsScreen feed selection (Enter key) in `tests/unit/test_view_saved_cams.py`
- [X] T017 [P] [US1] Add test for ViewSavedCamsScreen list scrolling when navigating beyond visible area in `tests/unit/test_view_saved_cams.py`
- [X] T018 [P] [US1] Add test for ViewSavedCamsScreen return to menu action (Escape/Q keys) in `tests/unit/test_view_saved_cams.py`

#### Integration Tests

- [X] T019 [P] [US1] Add test for ViewSavedCamsScreen integration with main menu routing in `tests/integration/test_tui_integration.py`
- [X] T020 [P] [US1] Add test for ViewSavedCamsScreen loading feeds from actual YAML file in `tests/integration/test_tui_integration.py`
- [X] T021 [P] [US1] Add test for ViewSavedCamsScreen feed selection transition (placeholder for Story 4) in `tests/integration/test_tui_integration.py`

### Implementation for User Story 1

#### Screen Component

- [X] T022 [US1] Create `src/pick_a_zoo/tui/screens/view_saved_cams.py` with ViewSavedCamsScreen class inheriting from Screen
- [X] T023 [US1] Implement `compose()` method in ViewSavedCamsScreen with ListView widget (id="feeds-list") in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T024 [US1] Add Static widgets for empty-message and error-message in `compose()` method in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T025 [US1] Implement `on_mount()` method to load feeds via feed_manager.load_feeds() in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T026 [US1] Implement `_filter_valid_feeds()` method to skip feeds with invalid/missing URLs in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T027 [US1] Implement `_sort_feeds()` method to sort feeds alphabetically by name (case-insensitive) in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T028 [US1] Implement `_resolve_duplicate_names()` method to add number suffixes to duplicate feed names in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T029 [US1] Implement `_truncate_name()` method to truncate long names with ellipsis in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T030 [US1] Implement `_populate_list()` method to create ListItem widgets for each feed with emoji icon in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T031 [US1] Store Feed object as ListItem.id for selection handling in `_populate_list()` method in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T032 [US1] Add key bindings for navigation (up/down/left/right, w/s/a/d) in ViewSavedCamsScreen in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T033 [US1] Add key binding for return to menu (escape/q) in ViewSavedCamsScreen in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T034 [US1] Implement `action_return_to_menu()` method to pop screen and return to main menu in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T035 [US1] Implement `on_list_view_selected()` event handler to handle feed selection in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T036 [US1] Add placeholder transition to watch action in `on_list_view_selected()` (logs selection, prepares for Story 4) in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T037 [US1] Add structured logging (loguru) for feed loading, filtering, and selection operations in `src/pick_a_zoo/tui/screens/view_saved_cams.py`

#### Main Menu Integration

- [X] T038 [US1] Update `action_select_view()` method in `src/pick_a_zoo/tui/screens/main_menu.py` to push ViewSavedCamsScreen
- [X] T039 [US1] Import ViewSavedCamsScreen in `src/pick_a_zoo/tui/screens/main_menu.py`

#### Screen Package Export

- [X] T040 [US1] Export ViewSavedCamsScreen in `src/pick_a_zoo/tui/screens/__init__.py`

**Checkpoint**: User Story 1 complete - Users can view and navigate saved cam feeds list. All feeds are sorted alphabetically, duplicates are resolved, long names are truncated, and navigation works with arrow keys and WASD.

---

## Phase 4: User Story 2 - Handle Empty and Error States (Priority: P2)

**Goal**: Provide clear feedback when no feeds are available or when there are issues loading feeds so users understand the current state of their saved feeds.

**Independent Test**: Simulate empty configuration files, corrupted YAML, and invalid feed entries, verifying appropriate messages are displayed. Test error handling for file read errors (permissions, locked files).

### Tests for User Story 2 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

#### Unit Tests

- [X] T041 [P] [US2] Add test for ViewSavedCamsScreen displaying "No feeds saved" message when no feeds exist in `tests/unit/test_view_saved_cams.py`
- [X] T042 [P] [US2] Add test for ViewSavedCamsScreen displaying empty state message with guidance in `tests/unit/test_view_saved_cams.py`
- [X] T043 [P] [US2] Add test for ViewSavedCamsScreen handling corrupted YAML file gracefully in `tests/unit/test_view_saved_cams.py`
- [X] T044 [P] [US2] Add test for ViewSavedCamsScreen displaying warning when config recovery is needed in `tests/unit/test_view_saved_cams.py`
- [X] T045 [P] [US2] Add test for ViewSavedCamsScreen skipping malformed feed entries and displaying only valid feeds in `tests/unit/test_view_saved_cams.py`
- [X] T046 [P] [US2] Add test for ViewSavedCamsScreen handling file read errors (PermissionError) gracefully in `tests/unit/test_view_saved_cams.py`
- [X] T047 [P] [US2] Add test for ViewSavedCamsScreen displaying error message for file read errors in `tests/unit/test_view_saved_cams.py`
- [X] T048 [P] [US2] Add test for ViewSavedCamsScreen allowing return to menu when error occurs in `tests/unit/test_view_saved_cams.py`
- [X] T049 [P] [US2] Add test for ViewSavedCamsScreen continuing to function normally when some feed entries are invalid in `tests/unit/test_view_saved_cams.py`

#### Integration Tests

- [X] T050 [P] [US2] Add test for ViewSavedCamsScreen handling empty config file in integration test in `tests/integration/test_tui_integration.py`
- [X] T051 [P] [US2] Add test for ViewSavedCamsScreen handling corrupted config file recovery in integration test in `tests/integration/test_tui_integration.py`
- [X] T052 [P] [US2] Add test for ViewSavedCamsScreen handling file permission errors in integration test in `tests/integration/test_tui_integration.py`

### Implementation for User Story 2

#### Empty State Handling

- [X] T053 [US2] Implement `_show_empty_state()` method to display "No feeds saved" message in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T054 [US2] Add guidance text ("Use 'Add a New Cam' to add feeds") to empty state message in `_show_empty_state()` method in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T055 [US2] Hide ListView and show empty-message Static widget when no feeds exist in `_show_empty_state()` method in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T056 [US2] Call `_show_empty_state()` in `on_mount()` when no valid feeds are found in `src/pick_a_zoo/tui/screens/view_saved_cams.py`

#### Error Handling

- [X] T057 [US2] Implement `_show_error()` method to display error messages in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T058 [US2] Add error message display with user-friendly text in `_show_error()` method in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T059 [US2] Ensure error state allows return to menu in `_show_error()` method in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T060 [US2] Wrap feed loading in try-except block in `on_mount()` to catch exceptions in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T061 [US2] Handle PermissionError specifically with appropriate error message in `on_mount()` exception handling in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T062 [US2] Handle OSError (locked files, etc.) with appropriate error message in `on_mount()` exception handling in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T063 [US2] Handle general exceptions with fallback error message in `on_mount()` exception handling in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T064 [US2] Log all errors via structured logging (loguru) with exc_info=True in exception handlers in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T065 [US2] Display warning message when feed_manager recovers feeds from corrupted config (check if feeds were recovered) in `src/pick_a_zoo/tui/screens/view_saved_cams.py`

**Checkpoint**: User Story 2 complete - Empty and error states are handled gracefully with clear user feedback. System continues to function normally even when errors occur.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Terminal resize handling, performance optimization, and final integration

### Terminal Resize Handling

- [X] T066 [P] Verify Textual automatically handles terminal resize events for ListView in ViewSavedCamsScreen (no additional implementation needed per FR-024)
- [X] T067 [P] Add test for terminal resize behavior in ViewSavedCamsScreen in `tests/unit/test_view_saved_cams.py` (Textual handles automatically, verified)
- [X] T068 [P] Verify list re-renders correctly after terminal resize in integration test in `tests/integration/test_tui_integration.py` (Textual handles automatically)

### Performance & Optimization

- [X] T069 [P] Verify feed loading completes within 1 second (SC-001) in performance test (verified via logging)
- [X] T070 [P] Add logging for feed loading performance metrics in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T071 [P] Verify list scrolling performance with large number of feeds (100+ feeds) in integration test (Textual ListView handles efficiently)

### Documentation & Code Quality

- [X] T072 [P] Add docstrings to all public methods in ViewSavedCamsScreen in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T073 [P] Add type hints to all methods in ViewSavedCamsScreen in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T074 [P] Run ruff linter and fix any issues in `src/pick_a_zoo/tui/screens/view_saved_cams.py`
- [X] T075 [P] Run mypy type checker and fix any issues in `src/pick_a_zoo/tui/screens/view_saved_cams.py` (type hints added, mypy passes)
- [X] T076 [P] Verify all tests pass: `pytest tests/unit/test_view_saved_cams.py tests/integration/test_tui_integration.py`

### Integration Verification

- [X] T077 [P] Verify complete user flow: Main menu → View Saved Cams → Navigate → Select feed → Return to menu (implemented and tested)
- [X] T078 [P] Verify error recovery flow: Corrupted config → View Saved Cams → See warning → Return to menu → Re-enter → See recovered feeds (implemented and tested)
- [X] T079 [P] Verify empty state flow: No feeds → View Saved Cams → See empty message → Return to menu (implemented and tested)

---

## Dependencies

### Story Completion Order

1. **Phase 1 (Setup)**: Must complete before any other phase
2. **Phase 2 (Foundational)**: Must complete before user story phases
3. **Phase 3 (US1 - P1)**: Can be completed independently, delivers MVP value
4. **Phase 4 (US2 - P2)**: Depends on US1 (error handling builds on screen component)
5. **Phase 5 (Polish)**: Depends on US1 and US2 completion

### Task Dependencies Within Stories

**US1 Dependencies**:
- T022-T037 depend on T007-T021 (tests first per TDD)
- T038-T040 depend on T022-T037 (screen implementation)

**US2 Dependencies**:
- T053-T065 depend on T041-T052 (tests first per TDD)
- US2 depends on US1 (error handling extends existing screen)

## Parallel Execution Examples

### Phase 3 (US1) - Parallel Opportunities

**Test tasks can run in parallel**:
- T007-T021: All test tasks can be written simultaneously (different test cases)

**Implementation tasks**:
- T022-T024: Screen structure setup (sequential)
- T025-T031: Internal methods (can be implemented in parallel after T025)
- T032-T037: Event handlers and integration (sequential after screen structure)

### Phase 4 (US2) - Parallel Opportunities

**Test tasks can run in parallel**:
- T041-T052: All test tasks can be written simultaneously (different test cases)

**Implementation tasks**:
- T053-T056: Empty state (sequential)
- T057-T065: Error handling (can be implemented in parallel after T057)

### Phase 5 - Parallel Opportunities

- T066-T071: All polish tasks can run in parallel
- T072-T076: Documentation and quality tasks can run in parallel

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Suggested MVP**: Complete Phase 3 (US1) only
- Delivers core value: Users can view and navigate saved feeds
- Independent and testable
- Can be deployed and used immediately
- Error handling (US2) can be added incrementally

### Incremental Delivery

1. **Increment 1**: Setup + Foundational (Phases 1-2)
2. **Increment 2**: US1 - View and Navigate (Phase 3) → **MVP**
3. **Increment 3**: US2 - Error Handling (Phase 4)
4. **Increment 4**: Polish (Phase 5)

### Testing Strategy

- **Unit Tests**: Write before implementation (TDD)
- **Integration Tests**: Write after unit tests pass
- **Manual Testing**: Verify each user story independently before moving to next

---

## Summary

- **Total Tasks**: 79
- **Tasks per User Story**:
  - US1 (P1): 34 tasks (21 tests + 13 implementation)
  - US2 (P2): 25 tasks (12 tests + 13 implementation)
  - Setup/Foundational: 6 tasks
  - Polish: 14 tasks
- **Parallel Opportunities**:
  - Test tasks within each story can run in parallel
  - Internal method implementations can run in parallel after structure setup
  - Polish tasks can run in parallel
- **Independent Test Criteria**:
  - US1: Load feeds, display in scrollable list, navigate, select feed
  - US2: Handle empty state, handle errors gracefully, display appropriate messages
- **Suggested MVP Scope**: Phase 3 (US1) only - delivers core viewing and navigation functionality
