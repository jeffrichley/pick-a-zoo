
# Story 2 — Add a New Live Cam Feed
## /plan

## 🏗 Architectural Overview
This story extends feed_manager with feed discovery logic and adds a Textual screen to collect name + URL inputs.

## 🧰 Technologies Used
- httpx — fetch page/streams
- beautifulsoup4 + lxml — HTML parsing
- m3u8 — playlist handling
- PyYAML — config persistence
- pydantic — validation

## 📦 File & Module Layout
```
core/
  feed_manager.py (add: extract_streams, add_feed)
tui/screens/
  add_cam.py
```

## 🔌 Internal Interfaces
- feed_manager.extract_streams(url) -> list[str]
- feed_manager.add_feed(name, url)

## ⚙️ Implementation Steps
1. Build add_cam Textual screen.
2. Create extraction pipeline: direct check → HTML parsing → video tags.
3. Handle multiple stream selection.
4. Save to feeds.yaml atomically.

## 🧪 Testing
- Mock httpx responses.
- HTML parsing tests with sample pages.
- YAML save/load tests.

## 🔮 Extensibility
- Add auto-thumbnail fetch.
