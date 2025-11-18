
# Story 4 — Launch Video Window for Selected Cam
## /specify

## 🎯 Summary
Open a GUI window displaying the selected live stream while keeping the TUI open.

## 🧠 Why This Matters
This is the core "watch" experience and demonstrates multi-window architecture.

## 🔍 User Story
> “As a user, I want the selected cam to open in a window so I can watch live video.”

## 📌 Acceptance Criteria
- Clicking “Watch Cam” opens PyQt window.
- Video plays automatically.
- Window can be resized.
- Resized dimensions saved to YAML.

## 📂 Data Requirements
- Read feed url.
- Persist updated window_size.

## 🛣️ Primary Flow
1. User selects feed.
2. PyQt window launches.
3. Stream begins playing.
4. User may resize window.

## 🔄 Alternate Flows
- Stream unavailable → window shows friendly error.
