# Tasks: Launch the Pick-a-Zoo TUI

**Input**: Design documents from `/specs/001-launch-tui/`
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

**Purpose**: Project initialization and basic structure

- [X] T001 Create project directory structure: `src/pick_a_zoo/`, `src/pick_a_zoo/core/`, `src/pick_a_zoo/tui/`, `src/pick_a_zoo/tui/screens/`, `tests/unit/`, `tests/integration/`
- [X] T002 Create `src/pick_a_zoo/__init__.py` with package initialization
- [X] T003 [P] Create `src/pick_a_zoo/core/__init__.py` with core package initialization
- [X] T004 [P] Create `src/pick_a_zoo/tui/__init__.py` with tui package initialization
- [X] T005 [P] Create `src/pick_a_zoo/tui/screens/__init__.py` with screens package initialization
- [X] T006 [P] Verify all dependencies from pyproject.toml are installed (textual, rich, PyYAML, pydantic, platformdirs, loguru)
- [X] T007 [P] Configure pytest in pyproject.toml (already configured, verify testpaths and markers)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Models (Pydantic)

- [X] T008 [P] Create `src/pick_a_zoo/core/models.py` with WindowSize Pydantic model (width: int > 0, height: int > 0)
- [X] T009 [P] Create Feed Pydantic model in `src/pick_a_zoo/core/models.py` (name: str, url: str, window_size: WindowSize | None)
- [X] T010 [P] Add URL validation to Feed model using Pydantic HttpUrl or custom validator in `src/pick_a_zoo/core/models.py`
- [X] T011 [P] Add non-empty string validation for Feed.name in `src/pick_a_zoo/core/models.py`

### Feed Manager Library (Constitution: Library-First)

- [X] T012 Create `src/pick_a_zoo/core/feed_manager.py` with `get_config_path() -> Path` function using platformdirs
- [X] T013 Implement `load_feeds() -> list[Feed]` function in `src/pick_a_zoo/core/feed_manager.py` with YAML parsing and error handling
- [X] T014 Implement missing file handling in `load_feeds()` - create empty file with default YAML structure in `src/pick_a_zoo/core/feed_manager.py`
- [X] T015 Implement corrupted file handling in `load_feeds()` - rebuild empty file and log warning in `src/pick_a_zoo/core/feed_manager.py`
- [X] T016 Implement `save_feeds(feeds: list[Feed]) -> None` function with atomic write pattern in `src/pick_a_zoo/core/feed_manager.py`
- [X] T017 Add structured logging (loguru) to all feed_manager functions in `src/pick_a_zoo/core/feed_manager.py`
- [X] T018 Add Feed validation before saving in `save_feeds()` function in `src/pick_a_zoo/core/feed_manager.py`

**Checkpoint**: Foundation ready - Feed and WindowSize models exist, feed_manager library is functional and independently testable. User story implementation can now begin.

---

## Phase 3: User Story 1 - Launch TUI and Navigate Menu (Priority: P1) 🎯 MVP

**Goal**: Launch a beautiful TUI that lists all available actions so users can navigate the system easily without remembering commands.

**Independent Test**: Launch the application (`pickazoo` command) and verify the TUI appears with all menu options visible and navigable. Test navigation with arrow keys, WASD keys, and hotkey shortcuts. Verify graceful handling of missing/corrupted config files.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

#### Unit Tests

- [X] T019 [P] [US1] Create unit test file `tests/unit/test_feed_manager.py` with test for `load_feeds()` with valid YAML
- [X] T020 [P] [US1] Add test for `load_feeds()` with missing file in `tests/unit/test_feed_manager.py`
- [X] T021 [P] [US1] Add test for `load_feeds()` with corrupted YAML file in `tests/unit/test_feed_manager.py`
- [X] T022 [P] [US1] Add test for `save_feeds()` with valid feeds list in `tests/unit/test_feed_manager.py`
- [X] T023 [P] [US1] Add test for `save_feeds()` atomic write pattern in `tests/unit/test_feed_manager.py`
- [X] T024 [P] [US1] Add test for `get_config_path()` cross-platform path resolution in `tests/unit/test_feed_manager.py`
- [X] T025 [P] [US1] Create unit test file `tests/unit/test_main_menu.py` with test for MainMenuScreen rendering
- [X] T026 [P] [US1] Add test for MainMenuScreen keyboard navigation (arrow keys) in `tests/unit/test_main_menu.py`
- [X] T027 [P] [US1] Add test for MainMenuScreen WASD fallback navigation in `tests/unit/test_main_menu.py`
- [X] T028 [P] [US1] Add test for MainMenuScreen hotkey shortcuts in `tests/unit/test_main_menu.py`
- [X] T029 [P] [US1] Add test for MainMenuScreen quit action in `tests/unit/test_main_menu.py`
- [X] T030 [P] [US1] Add test for MainMenuScreen display of "No cams saved yet" message in `tests/unit/test_main_menu.py`
- [X] T031 [P] [US1] Add test for MainMenuScreen terminal size warning in `tests/unit/test_main_menu.py`

#### Integration Tests

- [X] T032 [P] [US1] Create integration test file `tests/integration/test_tui_integration.py` with test for app startup flow
- [X] T033 [P] [US1] Add test for feed loading integration on app startup in `tests/integration/test_tui_integration.py`
- [X] T034 [P] [US1] Add test for missing config file recovery in `tests/integration/test_tui_integration.py`
- [X] T035 [P] [US1] Add test for corrupted config file recovery in `tests/integration/test_tui_integration.py`

### Implementation for User Story 1

#### CLI Entry Point

- [X] T036 [US1] Create `src/pick_a_zoo/cli.py` with `main()` function that instantiates PickAZooApp and calls `run()`
- [X] T037 [US1] Configure `pickazoo` command entry point in pyproject.toml pointing to `pick_a_zoo.cli:main`

#### TUI Application Root

- [X] T038 [US1] Create `src/pick_a_zoo/tui/app.py` with PickAZooApp class inheriting from textual.app.App
- [X] T039 [US1] Implement `on_mount()` method in PickAZooApp to push MainMenuScreen in `src/pick_a_zoo/tui/app.py`
- [X] T040 [US1] Add key binding for 'q' to quit application in PickAZooApp in `src/pick_a_zoo/tui/app.py`
- [X] T041 [US1] Add key binding for 'escape' to quit application in PickAZooApp in `src/pick_a_zoo/tui/app.py`

#### Main Menu Screen

- [X] T042 [US1] Create `src/pick_a_zoo/tui/screens/main_menu.py` with MainMenuScreen class inheriting from textual.screen.Screen
- [X] T043 [US1] Implement menu options list in MainMenuScreen: "View Saved Cams", "Add a New Cam", "Watch a Cam", "Quit" in `src/pick_a_zoo/tui/screens/main_menu.py`
- [X] T044 [US1] Implement centered menu layout with visual hierarchy in MainMenuScreen in `src/pick_a_zoo/tui/screens/main_menu.py`
- [X] T045 [US1] Implement `on_mount()` method in MainMenuScreen to load feeds via `feed_manager.load_feeds()` in `src/pick_a_zoo/tui/screens/main_menu.py`
- [X] T046 [US1] Display feed count in MainMenuScreen if feeds exist in `src/pick_a_zoo/tui/screens/main_menu.py`
- [X] T047 [US1] Display "No cams saved yet" message in MainMenuScreen if no feeds exist in `src/pick_a_zoo/tui/screens/main_menu.py`
- [X] T048 [US1] Implement arrow key navigation (↑↓) for menu options in MainMenuScreen in `src/pick_a_zoo/tui/screens/main_menu.py`
- [X] T049 [US1] Implement WASD fallback navigation (W=up, S=down) for menu options in MainMenuScreen in `src/pick_a_zoo/tui/screens/main_menu.py`
- [X] T050 [US1] Implement hotkey shortcuts: '1', '2', '3', '4' for direct menu selection in MainMenuScreen in `src/pick_a_zoo/tui/screens/main_menu.py`
- [X] T051 [US1] Implement hotkey shortcuts: 'v' (View), 'a' (Add), 'w' (Watch), 'q' (Quit) in MainMenuScreen in `src/pick_a_zoo/tui/screens/main_menu.py`
- [X] T052 [US1] Implement Enter key to confirm menu selection in MainMenuScreen in `src/pick_a_zoo/tui/screens/main_menu.py`
- [X] T053 [US1] Implement `action_select_option(option: str)` method for menu routing in MainMenuScreen in `src/pick_a_zoo/tui/screens/main_menu.py`
- [X] T054 [US1] Implement quit action that exits application in MainMenuScreen in `src/pick_a_zoo/tui/screens/main_menu.py`
- [X] T055 [US1] Implement terminal size detection and warning display in MainMenuScreen in `src/pick_a_zoo/tui/screens/main_menu.py`
- [X] T056 [US1] Implement scrollable/condensed layout adaptation when terminal size < 80x24 in MainMenuScreen in `src/pick_a_zoo/tui/screens/main_menu.py`
- [X] T057 [US1] Handle missing config file gracefully - display "No cams saved yet" and continue normally in MainMenuScreen in `src/pick_a_zoo/tui/screens/main_menu.py`
- [X] T058 [US1] Handle corrupted config file gracefully - display warning message and continue with empty feed list in MainMenuScreen in `src/pick_a_zoo/tui/screens/main_menu.py`
- [X] T059 [US1] Add structured logging (loguru) for TUI events in MainMenuScreen in `src/pick_a_zoo/tui/screens/main_menu.py`
- [X] T060 [US1] Ignore invalid key combinations gracefully (no action, no error) in MainMenuScreen in `src/pick_a_zoo/tui/screens/main_menu.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. The TUI launches, displays menu, handles navigation, and gracefully recovers from config file issues.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T061 [P] Verify all tests pass and provide adequate coverage
- [X] T062 [P] Run linting (ruff) and fix any issues across all source files
- [X] T063 [P] Run type checking (mypy) and fix any type issues across all source files
- [X] T064 [P] Verify performance goal: TUI launches within 1 second (SC-001)
- [X] T065 [P] Test cross-platform compatibility (Linux, macOS, Windows) for config file paths
- [X] T066 [P] Verify all acceptance scenarios from spec.md are covered by tests
- [X] T067 [P] Update README.md with installation and usage instructions
- [X] T068 [P] Verify quickstart.md examples work correctly
- [X] T069 [P] Code review for constitution compliance (all 5 principles)
- [X] T070 [P] Documentation review - ensure all public APIs are documented

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **Polish (Phase 4)**: Depends on User Story 1 completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within User Story 1

- Tests (T019-T035) MUST be written and FAIL before implementation
- Models (T008-T011) before feed_manager (T012-T018)
- Feed manager (T012-T018) before TUI components (T036-T060)
- CLI entry point (T036-T037) can be done in parallel with TUI components
- TUI App (T038-T041) before Main Menu Screen (T042-T060)
- Core functionality before error handling and polish

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003-T007)
- All Foundational model tasks marked [P] can run in parallel (T008-T011)
- All test tasks marked [P] can run in parallel (T019-T035)
- CLI entry point (T036-T037) can run in parallel with TUI App setup (T038-T041)
- Menu layout tasks (T043-T047) can run in parallel with navigation tasks (T048-T052)
- Error handling tasks (T055-T060) can run in parallel
- All Polish tasks marked [P] can run in parallel (T061-T070)

---

## Parallel Example: User Story 1

```bash
# Launch all unit tests for feed_manager together:
Task T019: "Create unit test file tests/unit/test_feed_manager.py with test for load_feeds() with valid YAML"
Task T020: "Add test for load_feeds() with missing file in tests/unit/test_feed_manager.py"
Task T021: "Add test for load_feeds() with corrupted YAML file in tests/unit/test_feed_manager.py"
Task T022: "Add test for save_feeds() with valid feeds list in tests/unit/test_feed_manager.py"
Task T023: "Add test for save_feeds() atomic write pattern in tests/unit/test_feed_manager.py"
Task T024: "Add test for get_config_path() cross-platform path resolution in tests/unit/test_feed_manager.py"

# Launch all unit tests for main_menu together:
Task T025: "Create unit test file tests/unit/test_main_menu.py with test for MainMenuScreen rendering"
Task T026: "Add test for MainMenuScreen keyboard navigation (arrow keys) in tests/unit/test_main_menu.py"
Task T027: "Add test for MainMenuScreen WASD fallback navigation in tests/unit/test_main_menu.py"
Task T028: "Add test for MainMenuScreen hotkey shortcuts in tests/unit/test_main_menu.py"
Task T029: "Add test for MainMenuScreen quit action in tests/unit/test_main_menu.py"
Task T030: "Add test for MainMenuScreen display of 'No cams saved yet' message in tests/unit/test_main_menu.py"
Task T031: "Add test for MainMenuScreen terminal size warning in tests/unit/test_main_menu.py"

# Launch all integration tests together:
Task T032: "Create integration test file tests/integration/test_tui_integration.py with test for app startup flow"
Task T033: "Add test for feed loading integration on app startup in tests/integration/test_tui_integration.py"
Task T034: "Add test for missing config file recovery in tests/integration/test_tui_integration.py"
Task T035: "Add test for corrupted config file recovery in tests/integration/test_tui_integration.py"

# Launch model creation together:
Task T008: "Create src/pick_a_zoo/core/models.py with WindowSize Pydantic model"
Task T009: "Create Feed Pydantic model in src/pick_a_zoo/core/models.py"
Task T010: "Add URL validation to Feed model using Pydantic HttpUrl or custom validator"
Task T011: "Add non-empty string validation for Feed.name in src/pick_a_zoo/core/models.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T018) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T019-T060)
   - Write tests first (T019-T035) - verify they FAIL
   - Implement models (T008-T011) if not done in Phase 2
   - Implement feed_manager (T012-T018) if not done in Phase 2
   - Implement CLI entry point (T036-T037)
   - Implement TUI App (T038-T041)
   - Implement Main Menu Screen (T042-T060)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Run `pickazoo` command
   - Verify TUI appears with menu
   - Test navigation (arrow keys, WASD, hotkeys)
   - Test config file scenarios (missing, corrupted)
   - Verify all tests pass
5. Complete Phase 4: Polish (T061-T070)
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: Write all tests for User Story 1 (T019-T035)
   - Developer B: Implement feed_manager library (T012-T018)
   - Developer C: Implement TUI App and Main Menu Screen (T038-T060)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [US1] label maps task to User Story 1 for traceability
- User Story 1 should be independently completable and testable
- Verify tests fail before implementing (Constitution Principle I - Test-First Development)
- Commit after each task or logical group
- Stop at checkpoint to validate story independently
- All tasks follow strict checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
