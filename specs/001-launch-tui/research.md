# Research: Launch the Pick-a-Zoo TUI

**Feature**: Launch the Pick-a-Zoo TUI
**Date**: 2024-12-19
**Phase**: 0 - Outline & Research

## Research Decisions

### Textual Framework Selection

**Decision**: Use Textual framework for TUI implementation

**Rationale**:
- Textual is a high-level, reactive, widget-based TUI framework that provides modern development patterns
- Built on Rich, which provides excellent rendering capabilities (colors, emojis, styled text)
- Supports full-screen TUI, keyboard navigation, hotkeys, and screen routing out of the box
- Well-documented and actively maintained
- Aligns with tech stack documentation in `plan/tech_stack.md`

**Alternatives considered**:
- **curses**: Lower-level, more complex, requires more boilerplate
- **prompt_toolkit**: Good for prompts but less suitable for full-screen applications
- **blessed**: Terminal wrapper but lacks widget system

### Configuration File Format

**Decision**: Use YAML format for configuration file (feeds.yaml)

**Rationale**:
- Human-readable and editable
- Supports nested structures (window_size with width/height)
- PyYAML provides robust parsing with error handling
- Standard format for configuration files
- Matches existing project documentation

**Alternatives considered**:
- **JSON**: Less human-friendly, no comments
- **TOML**: Good alternative but YAML already chosen in tech stack
- **INI**: Too simple for nested structures

### Data Model Validation

**Decision**: Use Pydantic for data model validation

**Rationale**:
- Automatic validation of Feed and WindowSize models
- Type safety and IDE support
- Built-in URL validation for feed URLs
- Clear error messages for invalid data
- Already in tech stack dependencies (`plan/tech_stack.md` mentions Pydantic for schema validation)
- Protects against corrupted YAML data by validating structure before use
- Aligns with Constitution Principle V (Observability & Simplicity) - structured validation reduces complexity

**Alternatives considered**:
- **Manual validation**: More error-prone, requires custom validation logic
- **dataclasses**: No built-in validation, would need custom validators
- **attrs**: Good alternative but Pydantic provides better validation and error messages

### Configuration File Location

**Decision**: Use platformdirs library to determine config file location

**Rationale**:
- Cross-platform support (Linux, macOS, Windows)
- Follows OS conventions for application data storage
- No hardcoded paths
- Already in tech stack dependencies

**Alternatives considered**:
- **Hardcoded paths**: Not cross-platform compatible
- **Environment variables**: Requires user configuration
- **Current directory**: Not appropriate for persistent data

### Error Handling Strategy

**Decision**: Graceful degradation with user-friendly messages

**Rationale**:
- Missing config: Create empty file, show "No cams saved yet" message
- Corrupted config: Detect parse errors, rebuild safe empty file, display warning
- Terminal size: Show warning but allow launch with adapted layout
- Follows FR-014: "System MUST gracefully handle all error conditions without crashing"

**Alternatives considered**:
- **Fail-fast**: Poor user experience, violates FR-014
- **Silent recovery**: Users unaware of issues, violates FR-011

### Navigation Fallback Strategy

**Decision**: WASD keys as fallback when arrow keys unavailable

**Rationale**:
- Common gaming convention (W=up, S=down, A=left, D=right)
- Widely understood by users
- Works on all terminals regardless of arrow key support
- Satisfies FR-003 requirement

**Alternatives considered**:
- **hjkl (vim-style)**: Less intuitive for non-vim users
- **Number keys**: Less discoverable
- **No fallback**: Violates accessibility requirements

### Terminal Size Handling

**Decision**: Display warning but allow launch with scrollable/condensed layout

**Rationale**:
- Maintains functionality even in constrained environments
- Better user experience than refusing to launch
- Allows users to resize terminal if needed
- Satisfies FR-016 requirement

**Alternatives considered**:
- **Refuse to launch**: Poor UX, blocks users unnecessarily
- **Auto-resize**: Not possible, terminal size is user-controlled

## Technology Integration Patterns

### Textual App Structure

**Pattern**: Single App class with Screen-based navigation

```python
# Pattern: App → Screen → Widgets
PickAZooApp (Textual App)
  └── MainMenuScreen (Textual Screen)
      └── Menu Widget (List of options)
```

**Rationale**: Textual's recommended architecture. Screens enable routing between different views (menu → add cam → watch cam).

### Feed Manager Library Pattern

**Pattern**: Standalone library module with clear interface

```python
# Library interface (constitution: library-first)
def load_feeds() -> list[Feed]:
    """Load feeds from YAML file. Returns empty list if file missing."""

def save_feeds(feeds: list[Feed]) -> None:
    """Save feeds to YAML file atomically."""
```

**Rationale**: Follows Constitution Principle II (Library-First Architecture). Module is independently testable and has single purpose.

### Configuration File Atomic Writes

**Pattern**: Write to temporary file, then rename atomically

**Rationale**: Prevents corruption if process crashes during write. Standard practice for configuration file updates.

## Unresolved Questions

None - all technical decisions resolved based on spec requirements and tech stack documentation.
