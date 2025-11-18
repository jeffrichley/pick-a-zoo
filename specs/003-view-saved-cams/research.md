# Research: View Saved Cam Feeds in TUI

**Feature**: View Saved Cam Feeds in TUI
**Date**: 2024-12-19
**Phase**: 0 - Outline & Research

## Research Decisions

### Textual ListView Widget Selection

**Decision**: Use Textual's ListView widget for displaying feeds list

**Rationale**:
- Textual ListView provides built-in scrolling, selection, and keyboard navigation
- Supports arrow keys and WASD fallback navigation out of the box
- Handles terminal resizing automatically
- Provides selection highlighting and Enter key handling
- Aligns with existing TUI architecture from Story 1 and Story 2
- Reduces implementation complexity compared to custom list rendering

**Alternatives considered**:
- **Custom widget**: More complex, requires manual scrolling and selection logic
- **DataTable**: Overkill for simple list, less intuitive for single-column data
- **Static list**: No built-in navigation, would require custom keyboard handling

### Duplicate Name Display Strategy

**Decision**: Display all duplicates with visual distinction (number suffix)

**Rationale**:
- Preserves all user data (no silent data loss)
- Clear visual distinction helps users differentiate feeds
- Consistent with Story 2's duplicate name resolution pattern
- Satisfies FR-021 requirement
- Simple to implement by checking existing names and appending suffix

**Alternatives considered**:
- **Skip duplicates silently**: Violates user expectation, loses data
- **Show warning**: Adds complexity, interrupts user flow
- **Display as-is**: Confusing for users, violates FR-021

### Long Name Truncation Strategy

**Decision**: Truncate long names with ellipsis

**Rationale**:
- Maintains list readability and consistent row height
- Standard pattern in list UIs
- Simple to implement with Textual's text rendering
- Satisfies FR-022 requirement
- Preserves most of the name for identification

**Alternatives considered**:
- **Wrap to multiple lines**: Breaks list layout, inconsistent row heights
- **Horizontal scroll**: Complex, poor UX for terminal
- **Show full name on hover**: Not supported in Textual, would require custom implementation

### Invalid URL Handling Strategy

**Decision**: Skip feeds with invalid or missing URLs silently

**Rationale**:
- Keeps list clean and functional
- Invalid URLs would fail during playback anyway (handled in Story 4)
- Prevents user confusion from broken entries
- Satisfies FR-013a requirement
- Simple validation during feed loading

**Alternatives considered**:
- **Display with warning icon**: Adds UI complexity, requires custom rendering
- **Show error message**: Clutters list, interrupts browsing
- **Display normally**: Misleading, would fail on selection

### File Modification Handling Strategy

**Decision**: Continue showing original list, refresh only on re-entry

**Rationale**:
- Prevents mid-session changes that could confuse users
- Stable UI during active viewing
- Refresh on explicit navigation provides predictable behavior
- Satisfies FR-023 requirement
- Avoids complex file watching or polling logic

**Alternatives considered**:
- **Auto-refresh on file change**: Complex, requires file watching, could interrupt user
- **Show notification**: Adds UI complexity, interrupts browsing
- **Lock file**: Prevents other processes, violates read-only requirement

### Terminal Resize Handling Strategy

**Decision**: Automatically adjust layout and re-render list

**Rationale**:
- Textual handles terminal resize events automatically
- Provides responsive UI that adapts to user's terminal size
- Standard behavior for Textual widgets
- Satisfies FR-024 requirement
- No additional implementation needed (Textual feature)

**Alternatives considered**:
- **Lock layout**: Poor UX, doesn't adapt to user needs
- **Show warning**: Unnecessary, Textual handles this automatically
- **Require restart**: Poor UX, violates responsive design principles

## Technology Integration Patterns

### Textual ListView Pattern

**Pattern**: ListView with ListItem widgets for each feed

```python
# Pattern: Screen → ListView → ListItem
ViewSavedCamsScreen (Textual Screen)
  └── ListView
      └── ListItem (for each Feed)
          └── Label (feed name with emoji)
```

**Rationale**: Textual's recommended pattern for scrollable lists. ListView handles scrolling, selection, and keyboard navigation automatically.

### Feed Loading Pattern

**Pattern**: Load feeds on screen mount, cache for session

```python
def on_mount(self):
    feeds = load_feeds()  # Load once on entry
    # Filter invalid entries
    valid_feeds = [f for f in feeds if f.url and is_valid_url(f.url)]
    # Sort alphabetically
    sorted_feeds = sorted(valid_feeds, key=lambda f: f.name)
    # Display in ListView
```

**Rationale**: Load once per screen entry (FR-023). Filter invalid entries (FR-013a). Sort alphabetically (FR-005). Cache in memory for session duration.

### Duplicate Name Resolution Pattern

**Pattern**: Check existing names, append number suffix

```python
def resolve_display_name(feed: Feed, all_feeds: list[Feed]) -> str:
    base_name = feed.name
    existing_names = {f.name for f in all_feeds if f != feed}
    
    if base_name not in existing_names:
        return base_name
    
    # Find highest suffix
    suffix = 2
    while f"{base_name} ({suffix})" in existing_names:
        suffix += 1
    
    return f"{base_name} ({suffix})"
```

**Rationale**: Simple algorithm that ensures unique display names. Handles existing suffixes correctly. Satisfies FR-021.

### Name Truncation Pattern

**Pattern**: Truncate with ellipsis based on terminal width

```python
def truncate_name(name: str, max_width: int) -> str:
    if len(name) <= max_width:
        return name
    return name[:max_width - 3] + "..."
```

**Rationale**: Simple string manipulation. Preserves most of name. Standard ellipsis pattern. Satisfies FR-022.

## Unresolved Questions

None - all technical decisions resolved based on spec requirements, clarifications, and existing codebase patterns.

