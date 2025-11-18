# 🐼 Pick-a-Zoo — **Tech Stack Overview**

Pick-a-Zoo is built using a modular, modern Python stack designed for clarity, extensibility, and a delightful demo experience.
The system is composed of three primary layers:

1. **TUI interface layer**
2. **Feed discovery + configuration layer**
3. **Video playback + snapshot GUI layer**

Below is the full technology breakdown.

---

## 🟣 1. **Terminal UI Layer**

### **Framework**

* **`textual`**
  A high-level, reactive, widget-based TUI framework that feels like building a web app—except entirely in the terminal.
  Used for:

  * Main menu
  * Feed listing
  * Add-feed workflow
  * Interactive UIs
  * Optional thumbnail previews

### **Rendering Engine**

* **`rich`**
  Provides emoji support, colored panels, styled text, and all text rendering under Textual.

### **Image-to-ASCII (optional thumbnails)**

* **`pillow`**
  Loads snapshot images for thumbnail generation.
* **textual + rich truecolor blocks**
  Convert images into ANSI half-block or ASCII art thumbnails shown directly in the terminal.

---

## 🟡 2. **Feed Discovery & Configuration Layer**

### **HTTP client**

* **`httpx`**
  Fast, async-friendly HTTP client used to:

  * Fetch web pages
  * Test stream URLs
  * Handle network errors cleanly

### **HTML parsing**

* **`beautifulsoup4`**
  Extracts video `<source>` URLs, `<video>` tags, or embedded player links when a user provides a webpage URL.
* **`lxml`** *(optional but recommended)*
  Faster, more robust HTML parsing.

### **Stream metadata helpers**

* **`m3u8`**
  Parses `.m3u8` playlists (HLS streams) for multi-variant feeds.

### **YAML configuration**

* **`PyYAML`**
  Loads and saves the `feeds.yaml` file that holds:

  ```yaml
  feeds:
    - name: "Panda Cam"
      url: "https://example/panda.m3u8"
      window_size:
        width: 1280
        height: 720
  ```

### **Schema validation**

* **`pydantic`**
  (Optional) Ensures feed entries are well-formed and protects against corrupted YAML.

### **Cross-platform config paths**

* **`platformdirs`**
  Determines where to store:

  * `feeds.yaml`
  * snapshots/
  * settings.yaml

### **Logging**

* **`loguru`**
  Clean, color-coded logs for debugging network issues and feed failures.

---

## 🟢 3. **Video Playback & Snapshot GUI Layer**

### **GUI framework**

* **`PyQt6`**
  Provides:

  * Video window
  * Toolbar buttons (Snapshot, Close)
  * Resizable playback window
  * Event handling (resize events → persist window size)

### **Video engine**

* **`ffpyplayer`** *(recommended)*
  Offers:

  * Reliable playback for many formats (HLS, RTSP, MP4, WebM)
  * Frame extraction for snapshots
  * FFmpeg-powered decoding
  * More consistent behavior than Qt’s built-in media player

### **Image handling**

* **`pillow`** again for saving snapshots:

  ```
  snapshots/<cam-name>-timestamp.jpg
  ```

---

## 🔧 4. **Utility Libraries**

* **`loguru`** — human-friendly logging
* **`platformdirs`** — OS-safe app data paths
* **`pydantic`** — crisp schema validation (optional but helpful)

---

## 🧪 5. **Full Installation via `uv`**

```bash
uv add \
    textual rich \
    httpx beautifulsoup4 lxml \
    PyYAML pydantic platformdirs \
    PyQt6 ffpyplayer pillow \
    loguru m3u8
```

---

## 🌉 Architecture Summary

Pick-a-Zoo combines a **modern TUI frontend**, a robust **stream discovery system**, and a **GUI-powered video player**.
Everything is intentionally separated into small feature modules to demonstrate the Spec-Kit way of building clean, extensible software.
