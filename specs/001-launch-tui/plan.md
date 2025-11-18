# Implementation Plan: Launch the Pick-a-Zoo TUI

**Branch**: `001-launch-tui` | **Date**: 2024-12-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-launch-tui/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Launch a beautiful terminal user interface (TUI) that serves as the main entry point for Pick-a-Zoo. The TUI displays a menu with four core actions (View Saved Cams, Add a New Cam, Watch a Cam, Quit) and provides intuitive navigation via arrow keys, WASD fallback, and hotkey shortcuts. The system gracefully handles missing or corrupted configuration files, ensuring a robust user experience. Built using Textual framework with Rich rendering, following library-first architecture principles.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: textual (TUI framework), rich (rendering engine), PyYAML (configuration file handling), pydantic (data model validation), platformdirs (cross-platform config paths), loguru (structured logging)
**Storage**: YAML configuration file (feeds.yaml) stored in platform-appropriate user data directory via platformdirs
**Testing**: pytest (unit tests), textual snapshot testing for TUI layout
**Target Platform**: Cross-platform terminal (Linux, macOS, Windows) supporting ANSI color codes
**Project Type**: single (CLI application)
**Performance Goals**: TUI launches within 1 second of command execution (SC-001)
**Constraints**: Terminal minimum size 80x24 (with graceful degradation), must handle missing/corrupted config files without crashing
**Scale/Scope**: Single-user desktop application, 4 menu options, configuration file with unlimited feed entries

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Test-First Development (NON-NEGOTIABLE)
✅ **COMPLIANT**: Plan includes unit tests for feed loading (valid YAML, missing file, corrupted file) and snapshot tests for menu layout. Tests will be written before implementation following TDD methodology.

### II. Library-First Architecture
✅ **COMPLIANT**: Feed manager (`feed_manager.py`) will be a standalone, independently testable library module. TUI components (`tui/app.py`, `tui/screens/main_menu.py`) are modular and self-contained.

### III. CLI Interface
✅ **COMPLIANT**: Application entry point (`pickazoo` command) provides CLI interface. Text I/O via terminal (stdout/stderr). Future features will expose functionality via CLI as well.

### IV. Integration Testing
✅ **COMPLIANT**: Integration tests will focus on feed manager contract tests and TUI-screen integration. Contract tests validate YAML parsing and file I/O operations.

### V. Observability & Simplicity
✅ **COMPLIANT**: Structured logging via loguru for all operations (config loading, error handling, TUI events). YAGNI principles applied - start with simple menu, avoid premature optimization.

**GATE STATUS**: ✅ **PASS** - All constitution principles satisfied. No violations detected.

## Project Structure

### Documentation (this feature)

```text
specs/001-launch-tui/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/pick_a_zoo/
├── __init__.py
├── cli.py               # CLI entry point (pickazoo command)
├── core/
│   ├── __init__.py
│   └── feed_manager.py  # Feed loading/saving library (constitution: library-first)
├── tui/
│   ├── __init__.py
│   ├── app.py           # Textual App root (PickAZooApp)
│   └── screens/
│       ├── __init__.py
│       └── main_menu.py  # Main menu screen (MainMenu)

tests/
├── unit/
│   ├── test_feed_manager.py  # Unit tests for feed_manager
│   └── test_main_menu.py     # Unit tests for menu screen
└── integration/
    └── test_tui_integration.py  # Integration tests for TUI flow
```

**Structure Decision**: Single project structure chosen. The `core/feed_manager.py` module follows library-first architecture (Constitution Principle II) - it's independently testable and has a clear single purpose. The `tui/` module contains TUI-specific components. CLI entry point in `cli.py` satisfies Constitution Principle III.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution principles are satisfied without requiring justification.
