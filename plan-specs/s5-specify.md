
# Story 5 — Take a Snapshot of the Live Feed
## /specify

## 🎯 Summary
Allow users to click a button in the viewer to capture a still frame.

## 🧠 Why This Matters
Snapshots are fun, useful, and demonstrate multimedia capture capabilities.

## 🔍 User Story
> “As a user, I want to take a snapshot of the current video frame so I can save cute moments.”

## 📌 Acceptance Criteria
- Snapshot button appears in video toolbar.
- Saves jpg with timestamp.
- Must work across different stream types.

## 📂 Data Requirements
- Snapshot directory.
- Filenames unique.

## 🛣️ Primary Flow
1. User clicks Snapshot.
2. System captures frame.
3. System saves jpg.
4. Temporary confirmation appears.

## 🔄 Alternate Flows
- Low FPS → fallback frame capture logic.
