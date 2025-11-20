# Tasks: Create Timelapse Video from Active Feed

**Input**: Design documents from `/specs/005-create-timelapse/`
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

**Purpose**: Project initialization and dependency setup

- [X] T001 Add imageio-ffmpeg dependency to pyproject.toml
- [X] T002 [P] Verify numpy dependency in pyproject.toml (already present)
- [X] T003 [P] Verify platformdirs dependency in pyproject.toml (already present)
- [X] T004 [P] Verify loguru dependency in pyproject.toml (already present)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 [P] Create timelapse_encoder.py module structure in src/pick_a_zoo/core/timelapse_encoder.py
- [X] T006 [P] Define TimelapseEncoderError exception class in src/pick_a_zoo/core/timelapse_encoder.py
- [X] T007 [P] Define RecordingInProgressError exception class in src/pick_a_zoo/core/timelapse_encoder.py
- [X] T008 [P] Define NoRecordingError exception class in src/pick_a_zoo/core/timelapse_encoder.py
- [X] T009 [P] Define EncodingError exception class in src/pick_a_zoo/core/timelapse_encoder.py
- [X] T010 [P] Define DiskSpaceError exception class in src/pick_a_zoo/core/timelapse_encoder.py
- [X] T011 Create TimelapseEncoder class skeleton with __init__() in src/pick_a_zoo/core/timelapse_encoder.py (depends on T005-T010)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Create Timelapse from Active Feed (Priority: P1) 🎯 MVP

**Goal**: Enable users to click a button in the video window to create a timelapse video from the currently playing feed at 5x speed.

**Independent Test**: Can be fully tested by opening a video feed, clicking the timelapse button, and verifying a timelapse video is created at 5x speed. This delivers immediate value by enabling users to create condensed video summaries.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T012 [P] [US1] Unit test for TimelapseEncoder.__init__() in tests/unit/test_timelapse_encoder.py
- [X] T013 [P] [US1] Unit test for TimelapseEncoder.start_recording() in tests/unit/test_timelapse_encoder.py
- [X] T014 [P] [US1] Unit test for TimelapseEncoder.capture_frame() in tests/unit/test_timelapse_encoder.py
- [X] T015 [P] [US1] Unit test for TimelapseEncoder.stop_recording() in tests/unit/test_timelapse_encoder.py
- [X] T016 [P] [US1] Unit test for TimelapseEncoder.is_recording() in tests/unit/test_timelapse_encoder.py
- [X] T017 [P] [US1] Unit test for TimelapseEncoder filename generation in tests/unit/test_timelapse_encoder.py
- [X] T018 [P] [US1] Unit test for TimelapseEncoder video encoding at 5x speed in tests/unit/test_timelapse_encoder.py
- [X] T019 [P] [US1] Unit test for VideoWindow timelapse button creation in tests/unit/test_video_window.py
- [X] T020 [P] [US1] Unit test for VideoWindow._on_timelapse_button_clicked() in tests/unit/test_video_window.py
- [X] T021 [P] [US1] Integration test for timelapse creation workflow in tests/integration/test_video_window_integration.py

### Implementation for User Story 1

- [X] T022 [US1] Implement TimelapseEncoder.__init__() with output directory setup in src/pick_a_zoo/core/timelapse_encoder.py (depends on T011)
- [X] T023 [US1] Implement TimelapseEncoder.start_recording() with feed_name and source_fps in src/pick_a_zoo/core/timelapse_encoder.py (depends on T022)
- [X] T024 [US1] Implement TimelapseEncoder.capture_frame() with frame validation in src/pick_a_zoo/core/timelapse_encoder.py (depends on T023)
- [X] T025 [US1] Implement TimelapseEncoder._encode_video() with imageio-ffmpeg at 5x fps in src/pick_a_zoo/core/timelapse_encoder.py (depends on T024)
- [X] T026 [US1] Implement TimelapseEncoder.stop_recording() with video file saving in src/pick_a_zoo/core/timelapse_encoder.py (depends on T025)
- [X] T027 [US1] Implement TimelapseEncoder.is_recording() in src/pick_a_zoo/core/timelapse_encoder.py (depends on T023)
- [X] T028 [US1] Implement TimelapseEncoder filename generation with timestamp in src/pick_a_zoo/core/timelapse_encoder.py (depends on T026)
- [X] T029 [US1] Implement VideoWindow._setup_timelapse_button() in src/pick_a_zoo/gui/video_window.py (depends on T022)
- [X] T030 [US1] Implement VideoWindow._on_timelapse_button_clicked() in src/pick_a_zoo/gui/video_window.py (depends on T029)
- [X] T031 [US1] Implement VideoWindow._start_timelapse_recording() in src/pick_a_zoo/gui/video_window.py (depends on T030, T023)
- [X] T032 [US1] Implement VideoWindow._stop_timelapse_recording() in src/pick_a_zoo/gui/video_window.py (depends on T031, T026)
- [X] T033 [US1] Implement VideoWindow._update_timelapse_button_state() for visual feedback in src/pick_a_zoo/gui/video_window.py (depends on T030)
- [X] T034 [US1] Extend VideoWindow._update_frame() to capture frames for timelapse in src/pick_a_zoo/gui/video_window.py (depends on T031, T024)
- [X] T035 [US1] Extend VideoWindow.closeEvent() to stop recording on window close in src/pick_a_zoo/gui/video_window.py (depends on T032)
- [X] T036 [US1] Add timelapse button to VideoWindow.__init__() layout in src/pick_a_zoo/gui/video_window.py (depends on T029)
- [X] T037 [US1] Add structured logging for timelapse operations in src/pick_a_zoo/core/timelapse_encoder.py (depends on T026)
- [X] T038 [US1] Add structured logging for timelapse button interactions in src/pick_a_zoo/gui/video_window.py (depends on T032)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can click the timelapse button, record frames, and save a 5x speed video.

---

## Phase 4: User Story 2 - Handle Timelapse Creation Errors Gracefully (Priority: P2)

**Goal**: Provide clear feedback when timelapse creation fails so users understand what went wrong and can take appropriate action.

**Independent Test**: Can be fully tested by simulating various error conditions (disk full, insufficient frames, encoding failures) and verifying appropriate error messages are displayed. This delivers value by providing clear feedback and preventing user confusion.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T039 [P] [US2] Unit test for disk space error handling in tests/unit/test_timelapse_encoder.py
- [ ] T040 [P] [US2] Unit test for encoding error handling in tests/unit/test_timelapse_encoder.py
- [ ] T041 [P] [US2] Unit test for non-playing feed error in tests/unit/test_video_window.py
- [ ] T042 [P] [US2] Unit test for partial recording save on error in tests/unit/test_timelapse_encoder.py
- [ ] T043 [P] [US2] Integration test for error scenarios in tests/integration/test_video_window_integration.py

### Implementation for User Story 2

- [ ] T044 [US2] Implement disk space check before starting recording in src/pick_a_zoo/core/timelapse_encoder.py (depends on T023)
- [ ] T045 [US2] Implement DiskSpaceError handling in TimelapseEncoder.start_recording() in src/pick_a_zoo/core/timelapse_encoder.py (depends on T044)
- [ ] T046 [US2] Implement encoding error handling with partial save in TimelapseEncoder.stop_recording() in src/pick_a_zoo/core/timelapse_encoder.py (depends on T026)
- [ ] T047 [US2] Implement error message display in VideoWindow for disk space errors in src/pick_a_zoo/gui/video_window.py (depends on T031, T045)
- [ ] T048 [US2] Implement error message display in VideoWindow for encoding errors in src/pick_a_zoo/gui/video_window.py (depends on T032, T046)
- [ ] T049 [US2] Implement validation for non-playing feed before starting recording in src/pick_a_zoo/gui/video_window.py (depends on T031)
- [ ] T050 [US2] Implement error message display for non-playing feed in src/pick_a_zoo/gui/video_window.py (depends on T049)
- [ ] T051 [US2] Implement error dismissal and window continuation in src/pick_a_zoo/gui/video_window.py (depends on T047, T048, T050)
- [ ] T052 [US2] Implement feed error detection and recording stop in VideoWindow._update_frame() in src/pick_a_zoo/gui/video_window.py (depends on T034)
- [ ] T053 [US2] Implement partial recording save on feed error in src/pick_a_zoo/gui/video_window.py (depends on T052, T026)
- [ ] T054 [US2] Add structured logging for error scenarios in src/pick_a_zoo/core/timelapse_encoder.py (depends on T045, T046)
- [ ] T055 [US2] Add structured logging for error scenarios in src/pick_a_zoo/gui/video_window.py (depends on T047, T048, T050)

**Checkpoint**: At this point, User Story 2 should be fully functional. All error scenarios are handled gracefully with clear user feedback.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final polish, edge case handling, and cross-cutting improvements

- [ ] T056 [P] Implement prevent multiple simultaneous recordings check in src/pick_a_zoo/core/timelapse_encoder.py
- [ ] T057 [P] Implement prevent multiple simultaneous recordings check in src/pick_a_zoo/gui/video_window.py
- [ ] T058 [P] Handle rapid button clicks gracefully in src/pick_a_zoo/gui/video_window.py
- [ ] T059 [P] Implement directory creation error handling in src/pick_a_zoo/core/timelapse_encoder.py
- [ ] T060 [P] Implement memory management for long recordings in src/pick_a_zoo/core/timelapse_encoder.py
- [ ] T061 [P] Handle resolution changes during recording in src/pick_a_zoo/core/timelapse_encoder.py
- [ ] T062 [P] Add success feedback message on timelapse completion in src/pick_a_zoo/gui/video_window.py
- [ ] T063 [P] Verify timelapse videos play correctly at 5x speed in manual testing
- [ ] T064 [P] Performance testing for timelapse creation without impacting playback
- [ ] T065 [P] Documentation updates for timelapse feature usage

---

## Dependencies

### User Story Completion Order

1. **Phase 1 (Setup)**: Must complete before any other work
2. **Phase 2 (Foundational)**: Must complete before user stories (blocking prerequisites)
3. **Phase 3 (US1)**: Can be implemented independently after Phase 2
4. **Phase 4 (US2)**: Depends on US1 completion (builds on error handling)
5. **Phase 5 (Polish)**: Can be done in parallel with US2 or after

### Task Dependencies Within Phases

**Phase 2**:
- T011 depends on T005-T010 (class skeleton needs exceptions defined)

**Phase 3 (US1)**:
- T022-T038 follow sequential dependencies (implementation builds on previous)
- Tests (T012-T021) can be written in parallel before implementation

**Phase 4 (US2)**:
- T044-T055 build on US1 implementation
- Error handling extends existing functionality

**Phase 5**:
- All tasks can be done in parallel (edge cases and polish)

## Parallel Execution Examples

### Phase 3 (US1) - Parallel Opportunities

**Test Writing (can all run in parallel)**:
- T012-T021: All test tasks can be written simultaneously

**Implementation (sequential dependencies)**:
- T022 → T023 → T024 → T025 → T026 (core encoder)
- T029 → T030 → T031 → T032 (button integration)
- T033, T034, T035, T036 can run after T032 completes

### Phase 4 (US2) - Parallel Opportunities

**Test Writing (can all run in parallel)**:
- T039-T043: All test tasks can be written simultaneously

**Implementation (mostly sequential)**:
- T044 → T045 (disk space)
- T046 (encoding errors, depends on T026)
- T047-T050 (error display, can run in parallel after dependencies)
- T051-T055 (error handling, sequential)

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**MVP includes**: Phase 1, Phase 2, Phase 3 (US1) only

This delivers:
- ✅ Timelapse button in video window
- ✅ Frame capture from active feed
- ✅ 5x speed video encoding
- ✅ Video file saving with timestamp naming
- ✅ Visual feedback during recording

**MVP excludes**: Phase 4 (US2) error handling polish (basic errors still handled, but not comprehensive)

### Incremental Delivery

1. **Increment 1 (MVP)**: Complete Phase 1-3
   - Users can create timelapse videos
   - Basic functionality works
   - Some error cases may not be fully handled

2. **Increment 2 (Error Handling)**: Complete Phase 4
   - Comprehensive error handling
   - Better user feedback
   - Robust edge case handling

3. **Increment 3 (Polish)**: Complete Phase 5
   - Edge cases handled
   - Performance optimized
   - Documentation complete

## Summary

- **Total Tasks**: 65 tasks
- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 7 tasks
- **Phase 3 (US1)**: 27 tasks (10 tests + 17 implementation)
- **Phase 4 (US2)**: 17 tasks (5 tests + 12 implementation)
- **Phase 5 (Polish)**: 10 tasks

- **Parallel Opportunities**: 
  - Test writing: 15 test tasks can be written in parallel
  - Setup tasks: 4 tasks can run in parallel
  - Foundational tasks: 6 of 7 can run in parallel
  - Polish tasks: All 10 can run in parallel

- **Independent Test Criteria**:
  - **US1**: Can be fully tested by opening a video feed, clicking the timelapse button, and verifying a timelapse video is created at 5x speed
  - **US2**: Can be fully tested by simulating various error conditions and verifying appropriate error messages are displayed

- **Suggested MVP Scope**: Phase 1, Phase 2, Phase 3 (US1) - 38 tasks total

- **Format Validation**: ✅ All tasks follow the checklist format with checkbox, ID, optional [P] marker, optional [Story] label, and file paths

