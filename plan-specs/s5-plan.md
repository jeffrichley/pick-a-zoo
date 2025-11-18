
# Story 5 — Take a Snapshot of the Live Feed
## /plan

## 🏗 Architecture
Snapshot capability is housed in the PyQt video player window.

## 🧰 Technologies
- ffpyplayer — get_frame()
- pillow — save image
- platformdirs — determine snapshot directory

## 📦 Layout
```
gui/player_window.py
snapshots/
```

## 🔌 Interfaces
- player_window.capture_frame()
- snapshot.save_image(array)

## ⚙️ Implementation Steps
1. Add Snapshot button to toolbar.
2. Use ffpyplayer.get_frame() to retrieve frame.
3. Convert frame to PIL Image.
4. Save with timestamp.
5. Show toast overlay.

## 🧪 Testing
- Save permissions.
- Corrupt frame handling.

## 🔮 Extensibility
- User-defined snapshot directory.
