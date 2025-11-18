
# Story 3 — View Saved Cam Feeds in TUI
## /specify

## 🎯 Summary
Display all saved cam feeds in a scrollable TUI list.

## 🧠 Why This Matters
Users need a simple way to browse and launch their saved cams.

## 🔍 User Story
> “As a user, I want to view all saved cams so I can choose which one to watch.”

## 📌 Acceptance Criteria
- Loads feeds from YAML.
- Sorted view.
- Selectable list with highlight.
- Selecting a feed triggers “Watch Cam”.

## 📂 Data Requirements
- Reads list of feeds from YAML.
- No writes in this story.

## 🛣️ Primary Flow
1. User opens “View Saved Cams”.
2. List of feeds appears.
3. User scrolls and selects one.
4. TUI transitions to watch action.

## 🔄 Alternate Flows
- Empty list → show “No feeds saved”.
