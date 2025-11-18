
# Story 4 — Launch Video Window for Selected Cam
## /plan

## 🏗 Architecture
Separate PyQt application/service launched from TUI command.

## 🧰 Technologies Used
- PyQt6 — GUI
- ffpyplayer — robust stream playback
- PyYAML — persist window size

## 📦 Layout
```
gui/
  player_window.py
core/
  feed_manager.py (update window size)
```

## 🔌 Interfaces
- player_window.play(url)
- feed_manager.update_window_size(name, size)

## ⚙️ Implementation Steps
1. Build PlayerWindow class.
2. Integrate ffpyplayer for video surface.
3. Emit resize events → save new size.
4. Launch via subprocess or thread-safe bridge from Textual.

## 🧪 Testing
- Manual stream sanity check.
- Mock feeds with test MP4 file.

