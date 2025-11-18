
# Story 6 — Simple Settings
## /plan

## 🏗 Architecture
A settings panel in Textual that reads/writes settings.yaml.

## 🧰 Technologies
- PyYAML — settings file
- platformdirs — path mgmt
- Textual — settings UI

## 📦 Layout
```
core/settings_manager.py
tui/screens/settings.py
```

## 🔌 Interfaces
- settings_manager.load_settings()
- settings_manager.save_settings()

## ⚙️ Implementation Steps
1. Build settings_manager with defaults.
2. Create SettingsScreen for TUI.
3. Bind inputs for resizing, theme, snapshot folder.
4. Save changes atomically.

## 🧪 Testing
- Validate YAML save/load.
- Theme switching behavior.

## 🔮 Extensibility
- Add per-feed override preferences.
