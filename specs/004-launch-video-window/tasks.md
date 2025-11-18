# Tasks: Launch Video Window for Selected Cam

**Input**: Design documents from `/specs/004-launch-video-window/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included per TDD methodology mentioned in plan.md constitution check. Tests should be written first and fail before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below use single project structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create gui/ directory structure in src/pick_a_zoo/
- [X] T002 [P] Create gui/__init__.py in src/pick_a_zoo/gui/__init__.py
- [X] T003 [P] Verify PyQt6 dependency in pyproject.toml (already present)
- [X] T004 [P] Verify ffpyplayer dependency in pyproject.toml (already present)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 [P] Implement validate_window_size() in src/pick_a_zoo/core/feed_manager.py
- [X] T006 [P] Implement get_validated_window_size() in src/pick_a_zoo/core/feed_manager.py
- [X] T007 [P] Implement get_feed_by_name() in src/pick_a_zoo/core/feed_manager.py
- [X] T008 Implement update_feed_window_size() in src/pick_a_zoo/core/feed_manager.py (depends on T005, T006, T007)
- [X] T009 [P] Create FeedNotFoundError exception in src/pick_a_zoo/core/feed_manager.py
- [X] T010 [P] Create video_player.py module structure in src/pick_a_zoo/core/video_player.py
- [X] T011 [P] Define VideoPlayerError exception class in src/pick_a_zoo/core/video_player.py
- [X] T012 [P] Define StreamLoadError exception class in src/pick_a_zoo/core/video_player.py
- [X] T013 [P] Define VideoFrame data class in src/pick_a_zoo/core/video_player.py
- [X] T014 [P] Define window dimension constants (DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT, MIN/MAX) in src/pick_a_zoo/core/video_player.py
- [X] T015 Create VideoPlayer class skeleton with __init__() in src/pick_a_zoo/core/video_player.py (depends on T010-T014)
- [X] T016 [P] Create video_window.py module structure in src/pick_a_zoo/gui/video_window.py
- [X] T017 [P] Create GUI thread management infrastructure in src/pick_a_zoo/tui/app.py (QApplication thread setup)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Launch Video Window and Play Stream (Priority: P1) 🎯 MVP

**Goal**: Enable users to select a saved cam feed and have it open in a separate window with automatic playback, while keeping the TUI functional.

**Independent Test**: Can be fully tested by selecting a feed from the saved feeds list and verifying a video window opens and begins playing the stream automatically. This delivers immediate value by enabling users to watch their saved camera feeds.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T018 [P] [US1] Unit test for VideoPlayer.__init__() in tests/unit/test_video_player.py
- [X] T019 [P] [US1] Unit test for VideoPlayer.load() with valid stream URL in tests/unit/test_video_player.py
- [X] T020 [P] [US1] Unit test for VideoPlayer.play() in tests/unit/test_video_player.py
- [X] T021 [P] [US1] Unit test for VideoPlayer.get_frame() in tests/unit/test_video_player.py
- [X] T022 [P] [US1] Unit test for VideoPlayer.stop() in tests/unit/test_video_player.py
- [X] T023 [P] [US1] Unit test for VideoWindow.__init__() in tests/unit/test_video_window.py
- [X] T024 [P] [US1] Unit test for VideoWindow.show() in tests/unit/test_video_window.py
- [X] T025 [P] [US1] Integration test for video window launching from TUI in tests/integration/test_video_window_integration.py

### Implementation for User Story 1

- [X] T026 [US1] Implement VideoPlayer.__init__() in src/pick_a_zoo/core/video_player.py (depends on T015)
- [X] T027 [US1] Implement VideoPlayer.load() with ffpyplayer integration in src/pick_a_zoo/core/video_player.py (depends on T026)
- [X] T028 [US1] Implement VideoPlayer.play() in src/pick_a_zoo/core/video_player.py (depends on T027)
- [X] T029 [US1] Implement VideoPlayer.get_frame() in src/pick_a_zoo/core/video_player.py (depends on T028)
- [X] T030 [US1] Implement VideoPlayer.stop() in src/pick_a_zoo/core/video_player.py (depends on T029)
- [X] T031 [US1] Implement VideoPlayer.is_playing() in src/pick_a_zoo/core/video_player.py (depends on T030)
- [X] T032 [US1] Implement VideoPlayer.get_error() in src/pick_a_zoo/core/video_player.py (depends on T031)
- [X] T033 [US1] Implement VideoWindow.__init__() in src/pick_a_zoo/gui/video_window.py (depends on T016, T026)
- [X] T034 [US1] Implement VideoWindow.show() with automatic playback in src/pick_a_zoo/gui/video_window.py (depends on T033, T027)
- [X] T035 [US1] Implement video frame rendering in VideoWindow in src/pick_a_zoo/gui/video_window.py (depends on T034, T029)
- [X] T036 [US1] Implement launch_video_window() function in src/pick_a_zoo/gui/video_window.py (depends on T035)
- [X] T037 [US1] Integrate video window launching in view_saved_cams.py screen in src/pick_a_zoo/tui/screens/view_saved_cams.py (depends on T036, T017)
- [X] T038 [US1] Add window tracking in TUI app for cleanup on exit in src/pick_a_zoo/tui/app.py (depends on T037)
- [X] T039 [US1] Add structured logging for video window operations in src/pick_a_zoo/gui/video_window.py (depends on T036)
- [X] T040 [US1] Add structured logging for video player operations in src/pick_a_zoo/core/video_player.py (depends on T032)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can select a feed and watch it in a separate window.

---

## Phase 4: User Story 2 - Resize Video Window and Persist Dimensions (Priority: P2)

**Goal**: Enable users to resize video windows and have those dimensions remembered per feed for future sessions.

**Independent Test**: Can be fully tested by resizing a video window, closing it, and verifying that when a new window opens, it uses the previously saved dimensions. This delivers value by providing a personalized, consistent viewing experience.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T041 [P] [US2] Unit test for validate_window_size() with valid dimensions in tests/unit/test_feed_manager.py
- [ ] T042 [P] [US2] Unit test for validate_window_size() with invalid dimensions in tests/unit/test_feed_manager.py
- [ ] T043 [P] [US2] Unit test for get_validated_window_size() in tests/unit/test_feed_manager.py
- [ ] T044 [P] [US2] Unit test for update_feed_window_size() in tests/unit/test_feed_manager.py
- [ ] T045 [P] [US2] Unit test for get_feed_by_name() in tests/unit/test_feed_manager.py
- [ ] T046 [P] [US2] Unit test for VideoWindow.resizeEvent() in tests/unit/test_video_window.py
- [ ] T047 [P] [US2] Unit test for VideoWindow.closeEvent() dimension persistence in tests/unit/test_video_window.py
- [ ] T048 [P] [US2] Integration test for window dimension persistence across sessions in tests/integration/test_video_window_integration.py

### Implementation for User Story 2

- [ ] T049 [US2] Implement window dimension loading from feed in VideoWindow.__init__() in src/pick_a_zoo/gui/video_window.py (depends on T033, T007)
- [ ] T050 [US2] Implement default dimension fallback (1280x720) in VideoWindow.__init__() in src/pick_a_zoo/gui/video_window.py (depends on T049)
- [ ] T051 [US2] Implement window dimension validation on load in VideoWindow.__init__() in src/pick_a_zoo/gui/video_window.py (depends on T050, T005)
- [ ] T052 [US2] Implement setMinimumSize(320, 240) and setMaximumSize(7680, 4320) in VideoWindow.__init__() in src/pick_a_zoo/gui/video_window.py (depends on T051)
- [ ] T053 [US2] Implement VideoWindow.resizeEvent() handler in src/pick_a_zoo/gui/video_window.py (depends on T052)
- [ ] T054 [US2] Implement resize event debouncing (500ms) in VideoWindow.resizeEvent() in src/pick_a_zoo/gui/video_window.py (depends on T053)
- [ ] T055 [US2] Implement VideoWindow.closeEvent() handler in src/pick_a_zoo/gui/video_window.py (depends on T054)
- [ ] T056 [US2] Implement dimension persistence in VideoWindow.closeEvent() calling update_feed_window_size() in src/pick_a_zoo/gui/video_window.py (depends on T055, T008)
- [ ] T057 [US2] Add error handling for configuration file write errors in VideoWindow.closeEvent() in src/pick_a_zoo/gui/video_window.py (depends on T056)
- [ ] T058 [US2] Add structured logging for dimension persistence operations in src/pick_a_zoo/gui/video_window.py (depends on T057)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can resize windows and have dimensions persist per feed.

---

## Phase 5: User Story 3 - Handle Stream Errors Gracefully (Priority: P3)

**Goal**: Provide clear, user-friendly error feedback when video streams cannot be played, allowing users to understand what went wrong and take appropriate action.

**Independent Test**: Can be fully tested by attempting to play an unavailable stream and verifying appropriate error messages are displayed in the video window. This delivers value by providing clear feedback and preventing user confusion.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T059 [P] [US3] Unit test for VideoPlayer.load() with unavailable stream URL in tests/unit/test_video_player.py
- [ ] T060 [P] [US3] Unit test for VideoPlayer.load() with invalid URL format in tests/unit/test_video_player.py
- [ ] T061 [P] [US3] Unit test for VideoPlayer.load() with network error in tests/unit/test_video_player.py
- [ ] T062 [P] [US3] Unit test for VideoPlayer.get_error() error retrieval in tests/unit/test_video_player.py
- [ ] T063 [P] [US3] Unit test for VideoWindow.display_error() in tests/unit/test_video_window.py
- [ ] T064 [P] [US3] Unit test for error display during stream loading failure in tests/unit/test_video_window.py
- [ ] T065 [P] [US3] Unit test for error display during connection loss in tests/unit/test_video_window.py
- [ ] T066 [P] [US3] Integration test for error handling with unavailable stream in tests/integration/test_video_window_integration.py

### Implementation for User Story 3

- [ ] T067 [US3] Implement error detection in VideoPlayer.load() for unavailable streams in src/pick_a_zoo/core/video_player.py (depends on T027)
- [ ] T068 [US3] Implement error detection in VideoPlayer.load() for invalid URL format in src/pick_a_zoo/core/video_player.py (depends on T067)
- [ ] T069 [US3] Implement error detection in VideoPlayer.load() for network errors in src/pick_a_zoo/core/video_player.py (depends on T068)
- [ ] T070 [US3] Implement error detection during playback (connection loss) in VideoPlayer.get_frame() in src/pick_a_zoo/core/video_player.py (depends on T029)
- [ ] T071 [US3] Implement user-friendly error message generation in VideoPlayer.get_error() in src/pick_a_zoo/core/video_player.py (depends on T032)
- [ ] T072 [US3] Implement VideoWindow.display_error() with QLabel overlay in src/pick_a_zoo/gui/video_window.py (depends on T033)
- [ ] T073 [US3] Integrate error display in VideoWindow.show() when stream loading fails in src/pick_a_zoo/gui/video_window.py (depends on T072, T067)
- [ ] T074 [US3] Integrate error display during playback when connection lost in VideoWindow in src/pick_a_zoo/gui/video_window.py (depends on T073, T070)
- [ ] T075 [US3] Ensure error windows remain closable (FR-012) in VideoWindow.display_error() in src/pick_a_zoo/gui/video_window.py (depends on T072)
- [ ] T076 [US3] Add structured logging for error events in src/pick_a_zoo/core/video_player.py (depends on T071)
- [ ] T077 [US3] Add structured logging for error display in src/pick_a_zoo/gui/video_window.py (depends on T075)

**Checkpoint**: All user stories should now be independently functional. Users can watch streams, resize windows with persistence, and receive clear error feedback.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T078 [P] Add docstrings to all public methods in src/pick_a_zoo/core/video_player.py
- [ ] T079 [P] Add docstrings to all public methods in src/pick_a_zoo/gui/video_window.py
- [ ] T080 [P] Add docstrings to new feed_manager methods in src/pick_a_zoo/core/feed_manager.py
- [ ] T081 [P] Code cleanup and refactoring across video player and window modules
- [ ] T082 [P] Performance optimization for video frame rendering in src/pick_a_zoo/gui/video_window.py
- [ ] T083 [P] Performance optimization for resize event debouncing in src/pick_a_zoo/gui/video_window.py
- [ ] T084 [P] Additional unit tests for edge cases in tests/unit/test_video_player.py
- [ ] T085 [P] Additional unit tests for edge cases in tests/unit/test_video_window.py
- [ ] T086 [P] Integration test for multiple simultaneous video windows in tests/integration/test_video_window_integration.py
- [ ] T087 [P] Integration test for TUI exit closing all video windows in tests/integration/test_video_window_integration.py
- [ ] T088 [P] Integration test for window dimension persistence with invalid saved values in tests/integration/test_video_window_integration.py
- [ ] T089 [P] Integration test for configuration file locking scenario (FR-016 edge case) in tests/integration/test_video_window_integration.py
- [ ] T090 [P] Integration test for off-screen window positioning edge case in tests/integration/test_video_window_integration.py
- [ ] T091 [P] Unit test for unsupported video codec handling edge case in tests/unit/test_video_player.py
- [ ] T092 Verify success criteria SC-001: Measure video window open time (target: <3s) via integration test in tests/integration/test_video_window_integration.py
- [ ] T093 Verify success criteria SC-002: Verify 100% auto-play rate via integration test in tests/integration/test_video_window_integration.py
- [ ] T094 Verify success criteria SC-003: Measure resize smoothness (no lag/stuttering) via manual testing checklist
- [ ] T095 Verify success criteria SC-004: Verify 100% dimension persistence rate via integration test in tests/integration/test_video_window_integration.py
- [ ] T096 Verify success criteria SC-005: Verify 100% dimension restore rate via integration test in tests/integration/test_video_window_integration.py
- [ ] T097 Verify success criteria SC-006: Measure error message display time (target: <2s) via integration test in tests/integration/test_video_window_integration.py
- [ ] T098 Verify success criteria SC-007: Verify 100% error window close success rate via integration test in tests/integration/test_video_window_integration.py
- [ ] T099 Verify success criteria SC-008: Verify TUI functionality while windows open via integration test in tests/integration/test_video_window_integration.py
- [ ] T100 Run linting and type checking on all new code
- [ ] T101 Update README.md with video window feature documentation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on User Story 1 for VideoWindow base functionality
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on User Story 1 for VideoWindow base functionality

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models/exceptions before core classes
- Core classes before GUI components
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Exception classes and constants marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members (with coordination for shared components)

---

## Parallel Example: User Story 1

```bash
# Launch all exception/constant definitions for User Story 1 together:
Task: "Define VideoPlayerError exception class in src/pick_a_zoo/core/video_player.py"
Task: "Define StreamLoadError exception class in src/pick_a_zoo/core/video_player.py"
Task: "Define VideoFrame data class in src/pick_a_zoo/core/video_player.py"
Task: "Define window dimension constants in src/pick_a_zoo/core/video_player.py"

# Launch all unit tests for User Story 1 together:
Task: "Unit test for VideoPlayer.__init__() in tests/unit/test_video_player.py"
Task: "Unit test for VideoPlayer.load() with valid stream URL in tests/unit/test_video_player.py"
Task: "Unit test for VideoPlayer.play() in tests/unit/test_video_player.py"
Task: "Unit test for VideoPlayer.get_frame() in tests/unit/test_video_player.py"
Task: "Unit test for VideoPlayer.stop() in tests/unit/test_video_player.py"
Task: "Unit test for VideoWindow.__init__() in tests/unit/test_video_window.py"
Task: "Unit test for VideoWindow.show() in tests/unit/test_video_window.py"
```

---

## Parallel Example: User Story 2

```bash
# Launch all feed_manager tests for User Story 2 together:
Task: "Unit test for validate_window_size() with valid dimensions in tests/unit/test_feed_manager.py"
Task: "Unit test for validate_window_size() with invalid dimensions in tests/unit/test_feed_manager.py"
Task: "Unit test for get_validated_window_size() in tests/unit/test_feed_manager.py"
Task: "Unit test for update_feed_window_size() in tests/unit/test_feed_manager.py"
Task: "Unit test for get_feed_by_name() in tests/unit/test_feed_manager.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (video window launching)
   - Developer B: User Story 2 (resize and persistence) - can start after US1 VideoWindow base is done
   - Developer C: User Story 3 (error handling) - can start after US1 VideoWindow base is done
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Window dimension validation uses bounds: 320x240 (min) to 7680x4320 (max)
- Default window dimensions: 1280x720
- All video windows run in same process, managed by single QApplication in separate thread
- TUI tracks all open windows and closes them on exit (FR-004b)

