# 🐼 **Pick-a-Zoo TUI Edition**

## **Detailed User Stories & Requirements**

Below are the fully elaborated user stories — each with clear triggers, flows, outcomes, and validations — ready for Spec-Kit planning and great for your demo.

---

# 📚 **Story 1 — Launch the Pick-a-Zoo TUI**

### **User Story**

> “As a user, I want to open a beautiful TUI that lists all available actions so I can navigate the system without remembering commands.”

### **What the TUI Shows**

* **View Saved Cams**
* **Add a New Cam**
* **Watch a Cam**
* **Quit**

### **Data Storage**

The app stores saved cam feeds in a YAML file:

```yaml
feeds:
  - name: "Panda Cam"
    url: "https://example/panda.m3u8"
    window_size:
      width: 1280
      height: 720
  - name: "Otter Live"
    url: "https://example/otter_stream.mp4"
```

**Storage Requirements:**
* YAML file automatically created if missing.
* Atomic writes (safe save to prevent corruption).
* Always produce valid YAML.
* Load feeds on app open.
* Detect and repair invalid YAML (graceful repair/regen, comment out bad entries).

### **Acceptance Criteria**

* TUI loads instantly.
* Navigation is arrow-keys or hotkeys.
* Layout uses clean sections and icons/emojis for charm.
* No crashes if the saved YAML is empty or corrupted (graceful repair/regen).

---

# 🐧 **Story 2 — Add a New Live Cam Feed**

### **User Story**

> “As a user, I want to add a new cam feed by providing a URL, and I want the app to automatically figure out if the URL is an actual camera stream or a webpage containing one.”

### **Primary Flow**

1. User chooses **Add Cam** in the TUI.
2. TUI prompts for:

   * **Cam Name**
   * **URL**
3. System determines:

   * If URL is **direct feed** (m3u8, mp4, webm, rtsp, etc.)
   * If URL is **HTML page** → fetch, parse HTML, extract `<video>` or `.m3u8` or embedded player links.
4. If multiple streams found → user chooses one.
5. System saves:

   ```yaml
   - name: "Panda Cam"
     url: "https://example.org/stream.m3u8"
   ```
6. Cam appears in the Saved Feeds list.

### **Alternate Flows**

* If no valid stream found → show error + let user retry.
* If internet fails → retry dialog.

### **Acceptance Criteria**

* YAML file automatically created if missing.
* Newly added cams persist across runs.
* Non-stream URLs are detected and errors communicated clearly.
* The feed extraction logic is robust and extendable.

---

# 🦦 **Story 3 — View Saved Cam Feeds in TUI**

### **User Story**

> “As a user, I want to see a clean list of all saved cams so I can select which one to watch.”

### **Details**

* Show cam names with small emoji icons.
* Selecting a cam triggers Story 4.

### **Acceptance Criteria**

* Correct sorting (alphabetical or recently added — your choice).
* No crashes if feeds are malformed in YAML.
* Clear highlighting when navigating.

---

# 🐘 **Story 4 — Launch Video Window for Selected Cam**

### **User Story**

> “As a user, I want the selected cam to open in its own window so I can actually watch the live stream in real time.”

### **Technical Notes**

* Use **PyQt6** (or PySide6 if licensing easier).
* Video rendered via:

  * `QMediaPlayer`
  * OR ffmpeg → Qt conversion if needed
* Window opens outside the TUI.

### **Data Storage**

Each cam's window size is persisted in the YAML file:

```yaml
feeds:
  - name: "Panda Cam"
    url: "https://example/panda.m3u8"
    window_size:
      width: 1280
      height: 720
```

**Window Size Behavior:**
* When a cam window is resized, the new dimensions are saved to YAML.
* On subsequent opens, the window restores to the last saved size.
* If no saved size exists, use default dimensions.

### **Flow**

1. User selects **Watch Cam** in the TUI.
2. A PyQt window appears:

   * Full video area.
   * A tiny toolbar with:

     * “Snapshot”
     * “Close”
3. TUI remains open (non-blocking).

### **Acceptance Criteria**

* Window must always appear on top of the TUI.
* Stream begins within 3 seconds if source is responsive.
* Handles RTSP, M3U8, MP4.
* No crash if the feed is temporarily down → show friendly message in window.
* Window size persists per cam (restores last saved dimensions on open).
* Window resize events update YAML atomically.

---

# 📸 **Story 5 — Take a Snapshot of the Live Feed**

### **User Story**

> “As a user, I want to click a button in the viewer window to save a still frame of the current video so I can capture cute moments.”

### **Flow**

1. User clicks **Snapshot** button.
2. System grabs current frame from PyQt video surface.
3. Saves as `snapshots/<cam-name>-timestamp.jpg`.
4. Temporary toast/overlay:
   **“Snapshot saved!”**

### **Acceptance Criteria**

* Works consistently on all supported camera formats.
* Non-blocking frame capture.
* Snapshot directory auto-created.
* Handles low-FPS or stuttering feeds gracefully.
* Filenames never conflict (always unique).

---

# 🎛️ **Story 6 — Simple Settings (Optional)**

* Default window size
* Default snapshot folder
* Autoplay on selection
* TUI theme (light/dark/solarized/“zoo mode”)

