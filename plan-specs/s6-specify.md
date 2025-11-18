
# Story 6 — Simple Settings
## /specify

## 🎯 Summary
Provide configurable defaults for window size, snapshot folder, autoplay, and TUI theme.

## 🧠 Why This Matters
Allows personalization and demonstrates config-driven behavior.

## 🔍 User Story
> “As a user, I want to adjust settings such as default window size or theme.”

## 📌 Acceptance Criteria
- Settings menu accessible from TUI.
- Editable defaults.
- Persisted in settings.yaml.

## 📂 Data Requirements
- settings.yaml storing window size, snapshot folder, theme.

## 🛣️ Primary Flow
1. User opens Settings.
2. User adjusts fields.
3. System saves new values.

## 🔄 Alternate Flows
- Invalid entries → error message.
