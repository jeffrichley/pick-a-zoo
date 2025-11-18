# Implementation Plan: View Saved Cam Feeds in TUI

**Branch**: `003-view-saved-cams` | **Date**: 2024-12-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-view-saved-cams/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Display all saved camera feeds in a scrollable, selectable TUI list. Users can navigate through feeds using arrow keys or WASD keys, view feeds sorted alphabetically by name, and select a feed to transition to the watch action. The system gracefully handles empty lists, corrupted configuration files, invalid feed entries, and terminal resizing. Built using Textual framework with Rich rendering, leveraging the existing feed_manager library for loading feeds, following library-first architecture principles.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: textual (TUI framework), rich (rendering engine), PyYAML (configuration file handling), pydantic (data model validation), platformdirs (cross-platform config paths), loguru (structured logging)
**Storage**: YAML configuration file (feeds.yaml) stored in platform-appropriate user data directory via platformdirs (read-only in this feature)
**Testing**: pytest (unit tests), textual snapshot testing for TUI layout
**Target Platform**: Cross-platform terminal (Linux, macOS, Windows) supporting ANSI color codes
**Project Type**: single (CLI application)
**Performance Goals**: Feeds list displays within 1 second of selecting "View Saved Cams" (SC-001)
**Constraints**: Terminal minimum size 80x24 (with graceful degradation), must handle empty/corrupted config files without crashing, must support terminal resizing, read-only viewing (no writes to config file)
**Scale/Scope**: Single-user desktop application, unlimited feed entries, list must scroll for feeds exceeding terminal height

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Test-First Development (NON-NEGOTIABLE)
✅ **COMPLIANT**: Plan includes unit tests for feed loading (valid YAML, missing file, corrupted file, invalid entries), duplicate name handling, long name truncation, empty state handling, and snapshot tests for list layout. Tests will be written before implementation following TDD methodology.

### II. Library-First Architecture
✅ **COMPLIANT**: Feed manager (`feed_manager.py`) is already a standalone, independently testable library module. The new TUI screen (`tui/screens/view_saved_cams.py`) will be modular and self-contained, using the feed_manager library for data loading without tight coupling.

### III. CLI Interface
✅ **COMPLIANT**: Feeds list screen integrates with existing CLI/TUI interface. Text I/O via terminal (stdout/stderr) through Textual framework. Navigation via arrow keys and WASD fallback.

### IV. Integration Testing
✅ **COMPLIANT**: Integration tests will focus on feed manager contract tests (loading feeds with various scenarios) and TUI-screen integration. Contract tests validate YAML parsing and feed loading operations.

### V. Observability & Simplicity
✅ **COMPLIANT**: Structured logging via loguru for all operations (feed loading, error handling, list navigation, selection). YAGNI principles applied - start with simple list view, avoid premature optimization for edge cases like very large feed lists.

**GATE STATUS**: ✅ **PASS** - All constitution principles satisfied. No violations detected.

## Project Structure

### Documentation (this feature)

```text
specs/003-view-saved-cams/
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
│   ├── feed_manager.py  # Feed loading library (existing, used by this feature)
│   └── models.py        # Pydantic models (existing)
├── tui/
│   ├── __init__.py
│   ├── app.py           # Textual App root (PickAZooApp)
│   └── screens/
│       ├── __init__.py
│       ├── main_menu.py  # Main menu screen (existing, will route to new screen)
│       └── view_saved_cams.py  # NEW: View saved cams screen (ViewSavedCamsScreen)

tests/
├── unit/
│   ├── test_feed_manager.py  # Unit tests for feed_manager (existing)
│   └── test_view_saved_cams.py  # NEW: Unit tests for view_saved_cams screen
└── integration/
    └── test_tui_integration.py  # Integration tests for TUI flow (existing, will extend)
```

**Structure Decision**: Single project structure chosen. The `core/feed_manager.py` module follows library-first architecture (Constitution Principle II) - it's independently testable and provides feed loading functionality. The `tui/screens/view_saved_cams.py` module contains TUI-specific components for displaying and navigating the feeds list. Integration with existing `feed_manager.py` maintains consistency with Story 1 and Story 2 architecture.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution principles are satisfied without requiring justification.
