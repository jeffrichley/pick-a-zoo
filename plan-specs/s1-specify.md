# Story 1 — Launch the Pick-a-Zoo TUI
## /specify

## 🎯 Summary
Provide a clean, attractive terminal UI that allows users to navigate the core features of Pick-a-Zoo without remembering commands.

## 🧠 Why This Matters
A TUI serves as the user’s main entry point.  
It simplifies onboarding, makes the demo fun, and highlights modularity in the architecture.

## 🔍 User Story
> “As a user, I want to open a beautiful TUI that lists all available actions so I can navigate the system easily.”

## 📌 Acceptance Criteria
- The TUI displays a menu with:
  - View Saved Cams
  - Add a New Cam
  - Watch a Cam
  - Quit
- User navigates with arrow keys or shortcuts.
- Launches instantly on startup.
- Recovers gracefully if no config file exists.
- Layout must be visually clear and inviting.

## 📂 Data / State Requirements (Non-Technical)
- Requires access to a list of saved cam feeds.
- The system must be able to detect missing or corrupted config and rebuild it.
- No additional data stored in this story.

## 🛣️ Primary Flow (User-Facing)
1. User runs `pickazoo` from the terminal.
2. A full-screen TUI appears.
3. A centered menu shows available actions.
4. User selects an option with arrow keys or hotkeys.
5. TUI routes to that feature’s screen.
6. User can press “q” to quit.

## 🔄 Alternate Flows
- If config is missing → show message "No cams saved yet."
- If YAML is invalid → show warning and rebuild a safe empty file.
