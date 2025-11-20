# Implementation Plan: Create Timelapse Video from Active Feed

**Branch**: `005-create-timelapse` | **Date**: 2025-11-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-create-timelapse/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add a timelapse button to the video window interface that allows users to create condensed video recordings from the currently playing feed at 5x normal speed. The feature captures frames from the active video feed, processes them at 5x speed (capturing every 5th frame or equivalent), and encodes them into a standard video format saved to a timelapses directory. Built using existing video player library for frame extraction, with a new timelapse encoder library module following library-first architecture principles, and PyQt6 button integration in the video window GUI.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: PyQt6 (GUI framework for video window button), ffpyplayer (video playback and frame extraction - existing), imageio-ffmpeg (video encoding for timelapse creation - selected after research), numpy (frame data manipulation - existing), platformdirs (cross-platform directory paths - existing), loguru (structured logging - existing)
**Storage**: File system (timelapse videos saved to `timelapses/` directory in application data directory, created automatically if missing)
**Testing**: pytest (unit tests), PyQt6 testing utilities for GUI components
**Target Platform**: Cross-platform desktop (Linux, macOS, Windows) with GUI support
**Project Type**: single (CLI application with GUI components)
**Performance Goals**: Timelapse recording starts within 1 second of button click (SC-001), visual feedback displayed within 500ms (SC-005), timelapse creation does not impact video playback performance (SC-009), error messages displayed within 2 seconds (SC-006)
**Constraints**: Must capture frames from active feed without interrupting playback, must encode at exactly 5x speed, must handle disk space errors gracefully, must prevent multiple simultaneous recordings, must save videos in standard format playable by common players, must handle feed errors gracefully and save partial recordings
**Scale/Scope**: Single-user desktop application, unlimited timelapse recordings, per-recording file management with timestamp-based naming

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Test-First Development (NON-NEGOTIABLE)
✅ **COMPLIANT**: Plan includes unit tests for timelapse encoder library (frame capture, 5x speed processing, video encoding, error handling), button interaction, recording state management, and file management. Tests will be written before implementation following TDD methodology.

### II. Library-First Architecture
✅ **COMPLIANT**: Timelapse encoding logic will be a standalone, independently testable library module (`core/timelapse_encoder.py`). GUI button components will be modular additions to `gui/video_window.py` that use the timelapse encoder library. The timelapse encoder library can be tested independently without GUI dependencies.

### III. CLI Interface
✅ **COMPLIANT**: Timelapse functionality integrates with existing CLI/TUI interface through video window GUI. Error messages and logging use structured text I/O via loguru. Timelapse videos are saved as files accessible via standard file system operations.

### IV. Integration Testing
✅ **COMPLIANT**: Integration tests will focus on timelapse encoder contract tests (frame capture from VideoPlayer, encoding at 5x speed, file saving), button-to-encoder integration, and video window-to-timelapse integration. Contract tests validate timelapse creation operations and file management.

### V. Observability & Simplicity
✅ **COMPLIANT**: Structured logging via loguru for all operations (button clicks, recording start/stop, frame capture, encoding progress, file saving, errors). YAGNI principles applied - start with basic frame capture and encoding, avoid premature optimization for advanced features like custom speed selection or video filters.

**GATE STATUS**: ✅ **PASS** - All constitution principles satisfied. No violations detected.

## Project Structure

### Documentation (this feature)

```text
specs/005-create-timelapse/
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
│   ├── video_player.py # Video player library (existing)
│   └── timelapse_encoder.py # NEW: Timelapse encoder library (library-first architecture)
├── gui/
│   ├── __init__.py
│   ├── player_launcher.py # Video window launcher (existing)
│   └── video_window.py  # PyQt6 video window component (existing, will add timelapse button)
└── tui/
    ├── __init__.py
    ├── app.py           # Textual App root (PickAZooApp)
    └── screens/
        ├── __init__.py
        ├── main_menu.py # Main menu screen (existing)
        ├── add_feed.py  # Add feed screen (existing)
        └── view_saved_cams.py  # View saved cams screen (existing)

tests/
├── unit/
│   ├── test_feed_manager.py  # Unit tests for feed_manager (existing)
│   ├── test_video_player.py  # Unit tests for video_player (existing)
│   ├── test_video_window.py # Unit tests for video_window (existing, will extend)
│   └── test_timelapse_encoder.py  # NEW: Unit tests for timelapse_encoder library
└── integration/
    ├── test_tui_integration.py  # Integration tests for TUI flow (existing)
    └── test_video_window_integration.py  # Integration tests for video window (existing, will extend)
```

**Structure Decision**: Single project structure chosen. The `core/timelapse_encoder.py` module follows library-first architecture (Constitution Principle II) - it's independently testable and provides timelapse encoding functionality without GUI dependencies. The `gui/video_window.py` module will be extended with PyQt6 button components that use the timelapse encoder library. This separation allows testing the timelapse encoding logic independently and enables future alternative GUI implementations if needed.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution principles are satisfied without requiring justification.
