# Implementation Plan: Launch Video Window for Selected Cam

**Branch**: `004-launch-video-window` | **Date**: 2024-12-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-launch-video-window/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Launch a separate GUI window displaying the selected live video stream while keeping the TUI open. Video windows are PyQt6 windows running in the same process as the TUI, managed by a single QApplication instance running in a separate thread. All windows are closed when the TUI exits. Windows support resizing with per-feed dimension persistence, automatic playback, and graceful error handling. Built using PyQt6 for GUI windows and ffpyplayer for video playback, following library-first architecture principles with a video player library module.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: PyQt6 (GUI framework for video windows), ffpyplayer (video playback engine supporting HLS, RTSP, MP4, WebM), PyYAML (configuration file handling), pydantic (data model validation), loguru (structured logging)
**Storage**: YAML configuration file (feeds.yaml) stored in `.pickazoo/` directory in current working directory (read and write for window dimensions)
**Testing**: pytest (unit tests), PyQt6 testing utilities for GUI components
**Target Platform**: Cross-platform desktop (Linux, macOS, Windows) with GUI support
**Project Type**: single (CLI application with GUI components)
**Performance Goals**: Video window opens and begins playing within 3 seconds of feed selection (SC-001), error messages displayed within 2 seconds (SC-006), smooth window resizing without lag (SC-003)
**Constraints**: Video windows must run in the same process as TUI using a single QApplication instance in a separate thread, must close all windows when TUI exits, must handle multiple simultaneous windows, must persist window dimensions per feed, must validate dimension bounds (320x240 to 7680x4320), must handle stream errors gracefully without crashing
**Scale/Scope**: Single-user desktop application, unlimited simultaneous video windows, per-feed window dimension preferences

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Test-First Development (NON-NEGOTIABLE)
✅ **COMPLIANT**: Plan includes unit tests for video player library (stream loading, playback, error handling), window dimension validation, configuration file updates, and GUI component behavior. Tests will be written before implementation following TDD methodology.

### II. Library-First Architecture
✅ **COMPLIANT**: Video player logic will be a standalone, independently testable library module (`core/video_player.py`). GUI window components (`gui/video_window.py`) will be modular and self-contained. The video player library can be tested independently without GUI dependencies.

### III. CLI Interface
✅ **COMPLIANT**: Video window launching integrates with existing CLI/TUI interface. Video windows are PyQt6 windows in the same process, managed by a QApplication instance running in a separate thread, and closed when TUI exits. Error messages and logging use structured text I/O via loguru.

### IV. Integration Testing
✅ **COMPLIANT**: Integration tests will focus on video player contract tests (stream loading, playback, error handling), window dimension persistence integration, and TUI-to-GUI window launching integration. Contract tests validate video playback operations and configuration file updates.

### V. Observability & Simplicity
✅ **COMPLIANT**: Structured logging via loguru for all operations (window creation, stream loading, playback events, errors, dimension persistence). YAGNI principles applied - start with basic video playback, avoid premature optimization for advanced features like video filters or custom controls.

**GATE STATUS**: ✅ **PASS** - All constitution principles satisfied. No violations detected.

## Project Structure

### Documentation (this feature)

```text
specs/004-launch-video-window/
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
│   ├── feed_manager.py  # Feed loading/saving library (existing)
│   ├── models.py       # Pydantic models (existing)
│   └── video_player.py # NEW: Video player library (library-first architecture)
├── gui/
│   ├── __init__.py
│   └── video_window.py  # NEW: PyQt6 video window component
└── tui/
    ├── __init__.py
    ├── app.py           # Textual App root (PickAZooApp)
    └── screens/
        ├── __init__.py
        ├── main_menu.py # Main menu screen (existing)
        ├── add_feed.py  # Add feed screen (existing)
        └── view_saved_cams.py  # View saved cams screen (existing, will launch video windows)

tests/
├── unit/
│   ├── test_feed_manager.py  # Unit tests for feed_manager (existing)
│   ├── test_video_player.py  # NEW: Unit tests for video_player library
│   └── test_video_window.py  # NEW: Unit tests for video_window GUI component
└── integration/
    ├── test_tui_integration.py  # Integration tests for TUI flow (existing, will extend)
    └── test_video_window_integration.py  # NEW: Integration tests for video window launching
```

**Structure Decision**: Single project structure chosen. The `core/video_player.py` module follows library-first architecture (Constitution Principle II) - it's independently testable and provides video playback functionality without GUI dependencies. The `gui/video_window.py` module contains PyQt6-specific GUI components that use the video_player library. This separation allows testing the video player logic independently and enables future alternative GUI implementations if needed.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution principles are satisfied without requiring justification.
