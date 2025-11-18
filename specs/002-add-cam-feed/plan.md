# Implementation Plan: Add a New Live Cam Feed

**Branch**: `002-add-cam-feed` | **Date**: 2024-12-19 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-add-cam-feed/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enable users to add new live camera feeds by providing a name and URL. The system automatically detects whether the URL is a direct stream (m3u8, mp4, webm, rtsp) or an HTML webpage containing embedded streams. For HTML pages, the system extracts playable stream URLs and presents them for user selection. All feeds are validated for accessibility immediately after URL entry and saved to the feeds.yaml configuration file. Built using httpx for HTTP requests, beautifulsoup4 for HTML parsing, and Textual for the TUI workflow, following library-first architecture principles.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: httpx (HTTP client), beautifulsoup4 (HTML parsing), lxml (HTML parser backend), m3u8 (HLS playlist parsing), PyYAML (configuration file handling), pydantic (data model validation), textual (TUI framework), rich (rendering engine), platformdirs (cross-platform config paths), loguru (structured logging)  
**Storage**: YAML configuration file (feeds.yaml) stored in platform-appropriate user data directory via platformdirs  
**Testing**: pytest (unit tests), textual snapshot testing for TUI screens  
**Target Platform**: Cross-platform terminal (Linux, macOS, Windows) supporting ANSI color codes  
**Project Type**: single (CLI application)  
**Performance Goals**: Direct stream feed addition completes in under 30 seconds (SC-001), HTML page feed addition completes in under 60 seconds (SC-003), URL validation timeout 10-30 seconds  
**Constraints**: Must handle network errors gracefully, support cancellation at any point, handle duplicate feed names automatically, validate URLs immediately after entry  
**Scale/Scope**: Single-user desktop application, unlimited feed entries, HTML pages up to reasonable parsing size

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Test-First Development (NON-NEGOTIABLE)
✅ **COMPLIANT**: Plan includes unit tests for URL detection (direct vs HTML), stream extraction from HTML, URL validation, duplicate name handling, and error scenarios. Tests will be written before implementation following TDD methodology.

### II. Library-First Architecture
✅ **COMPLIANT**: Feed discovery logic (`feed_discovery.py`) will be a standalone, independently testable library module. TUI components (`tui/screens/add_feed.py`) are modular and self-contained. Feed manager already follows library-first architecture.

### III. CLI Interface
✅ **COMPLIANT**: Feed addition workflow integrates with existing CLI/TUI interface. Text I/O via terminal (stdout/stderr) through Textual framework.

### IV. Integration Testing
✅ **COMPLIANT**: Integration tests will focus on feed discovery contract tests, URL validation integration, and TUI-screen integration. Contract tests validate HTML parsing and stream extraction operations.

### V. Observability & Simplicity
✅ **COMPLIANT**: Structured logging via loguru for all operations (URL validation, HTML parsing, stream extraction, feed saving). YAGNI principles applied - start with basic HTML parsing patterns, avoid premature optimization for edge cases like JavaScript rendering.

**GATE STATUS**: ✅ **PASS** - All constitution principles satisfied. No violations detected.

## Project Structure

### Documentation (this feature)

```text
specs/002-add-cam-feed/
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
│   ├── models.py        # Pydantic models (existing, may extend)
│   └── feed_discovery.py  # NEW: Feed discovery library (URL detection, HTML parsing, stream extraction)
├── tui/
│   ├── __init__.py
│   ├── app.py           # Textual App root (PickAZooApp)
│   └── screens/
│       ├── __init__.py
│       ├── main_menu.py  # Main menu screen (existing)
│       └── add_feed.py   # NEW: Add feed screen (AddFeedScreen)

tests/
├── unit/
│   ├── test_feed_manager.py  # Unit tests for feed_manager (existing)
│   ├── test_feed_discovery.py  # NEW: Unit tests for feed_discovery
│   └── test_add_feed.py      # NEW: Unit tests for add_feed screen
└── integration/
    ├── test_tui_integration.py  # Integration tests for TUI flow (existing)
    └── test_feed_discovery_integration.py  # NEW: Integration tests for feed discovery
```

**Structure Decision**: Single project structure chosen. The `core/feed_discovery.py` module follows library-first architecture (Constitution Principle II) - it's independently testable and has a clear single purpose (discovering and extracting streams from URLs). The `tui/screens/add_feed.py` module contains TUI-specific components for the add feed workflow. Integration with existing `feed_manager.py` maintains consistency with Story 1 architecture.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution principles are satisfied without requiring justification.
