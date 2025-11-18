# Story 1 — Launch the Pick-a-Zoo TUI
## /plan

## 🏗 Architectural Overview
This story creates the main entry interface to the app.
It will be a Textual-based TUI that delegates functionality to other modules:
- feed_manager (load/save feeds)
- tui/screens/menu.py (main menu)
- tui/app.py (root application)

## 🧰 Technologies Used
- **Textual** — main TUI framework
- **Rich** — rendering engine behind Textual
- **PyYAML** — loads/saves feed list for display
- **platformdirs** — determines config file location

## 📦 File & Module Layout
```
pickazoo/
  tui/
    app.py
    screens/
      main_menu.py
  data/
    feeds.yaml
  core/
    feed_manager.py
```

## 🔌 API / Interfaces (Internal)

### `feed_manager.load_feeds() -> list[Feed]`
Loads and parses YAML data.

### `MainMenu(Screen)`
Textual Screen displaying menu options.

## ⚙️ Implementation Steps

### Phase 1 — Textual App Setup
- Create `tui/app.py` with a `PickAZooApp` class.
- Register the main menu screen.

### Phase 2 — Main Menu Layout
- Implement a vertical list of menu actions.
- Add hotkey bindings (e.g. “A” for Add Cam).

### Phase 3 — Feed Loading Integration
- Call `load_feeds()` on startup.
- Display count of saved feeds.

### Phase 4 — Robust Error Handling
- Detect missing YAML and generate a clean default.
- Catch YAML parse errors and regenerate safely.

## 🧪 Testing Plan
- Unit test `load_feeds()` for:
  - valid YAML
  - missing file
  - corrupted file
- Manual test TUI rendering in terminal.
- Snapshot test for menu layout (text-based).

## 🔮 Extensibility Notes
- Add TUI themes.
- Add animated header/logo.
