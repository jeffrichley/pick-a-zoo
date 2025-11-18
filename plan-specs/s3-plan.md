
# Story 3 — View Saved Cam Feeds in TUI
## /plan

## 🏗 Architecture
A Textual screen rendering a list view populated by feed_manager.load_feeds().

## 🧰 Technologies
- Textual
- PyYAML

## 📦 Layout
```
tui/screens/
  list_cams.py
core/
  feed_manager.py
```

## 🔌 Interfaces
- load_feeds() -> list[Feed]
- CamListScreen.on_select()

## ⚙️ Implementation Steps
1. Create CamListScreen with ListView.
2. Load feeds from YAML on enter.
3. Convert each feed to a ListItem widget.
4. Handle “enter” key to launch Story 4.

## 🧪 Testing
- YAML load tests.
- TUI snapshot tests.
