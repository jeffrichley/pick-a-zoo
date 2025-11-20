# Research: Timelapse Video Creation

**Feature**: Create Timelapse Video from Active Feed
**Date**: 2025-11-20
**Phase**: 0 - Outline & Research

## Research Questions

### Q1: Video Encoding Library Selection

**Question**: What Python library should be used to encode captured frames into a video file at 5x speed?

**Context**: We need to capture frames from an active video feed (using existing VideoPlayer library) and encode them into a standard video format (MP4) that plays at 5x speed. The frames are already available as numpy arrays from ffpyplayer.

**Research Findings**:

**Option 1: imageio-ffmpeg**
- **Decision**: ✅ **SELECTED**
- **Rationale**: 
  - Lightweight wrapper around FFmpeg (which ffpyplayer already uses)
  - Simple API: `imageio.get_writer()` with fps parameter
  - Supports MP4 encoding with H.264 codec (standard, widely playable)
  - Can set frame rate directly (e.g., if source is 30fps, set output to 150fps for 5x speed)
  - Minimal dependencies (just imageio and ffmpeg)
  - Cross-platform support
  - Good performance for frame-by-frame encoding
- **Alternatives Considered**:
  - **opencv-python (cv2.VideoWriter)**: More complex API, requires codec configuration, but also viable
  - **ffmpeg-python**: Lower-level FFmpeg wrapper, more control but more complex
  - **imageio (without ffmpeg)**: Limited codec support, may not produce standard MP4 files
- **Implementation Approach**: Use `imageio.get_writer()` with `fps=source_fps*5` to create 5x speed video. Capture frames at source rate, encode at 5x frame rate.

**Option 2: Frame Capture Strategy**
- **Decision**: Capture every frame from VideoPlayer, encode at 5x frame rate
- **Rationale**:
  - VideoPlayer.get_frame() already provides frames at source rate
  - Simpler than skipping frames (which could miss important moments)
  - Encoding at 5x frame rate achieves 5x playback speed naturally
  - More consistent quality (no frame interpolation needed)
- **Alternatives Considered**:
  - **Capture every 5th frame**: Simpler but loses temporal information, may look choppy
  - **Frame interpolation**: More complex, not necessary for timelapse
- **Implementation Approach**: Capture all available frames from VideoPlayer, store in buffer, encode with fps=source_fps*5

**Option 3: File Format and Naming**
- **Decision**: MP4 format with H.264 codec, timestamp-based naming: `<feed-name>-YYYYMMDD-HHMMSS.mp4`
- **Rationale**:
  - MP4/H.264 is universally playable (standard video players)
  - Timestamp naming ensures uniqueness and provides chronological ordering
  - Format matches user expectations (standard video file)
- **Alternatives Considered**:
  - **WebM**: Good compression but less universal player support
  - **AVI**: Older format, larger file sizes
  - **Sequential numbering**: Less informative than timestamps
- **Implementation Approach**: Use imageio-ffmpeg with format='mp4', codec='libx264', save to timelapses directory

### Q2: Frame Buffer Management

**Question**: How should frames be buffered during recording - in memory or written to disk incrementally?

**Decision**: Buffer frames in memory with reasonable limit, flush to disk incrementally for long recordings
- **Rationale**:
  - Memory buffering is faster for short recordings
  - For very long recordings, need to flush periodically to prevent memory exhaustion
  - Can use a ring buffer or chunked encoding approach
- **Implementation Approach**: 
  - Buffer frames in memory list (numpy arrays)
  - When buffer reaches threshold (e.g., 1000 frames or 30 seconds), encode chunk and append to file
  - Final encoding combines all chunks or uses incremental encoding
  - For simplicity in MVP: buffer all frames, encode at end (acceptable for reasonable recording durations)

### Q3: Speed Calculation

**Question**: How to ensure exactly 5x speed in the output video?

**Decision**: Encode at 5x the source frame rate
- **Rationale**:
  - If source video is 30fps, encode output at 150fps
  - When played back at normal speed (30fps), it will appear 5x faster
  - Alternatively: encode at source fps but set playback speed metadata (less reliable)
- **Implementation Approach**: 
  - Detect source frame rate from VideoPlayer (or use default 30fps if unknown)
  - Set output fps = source_fps * 5
  - Encode all captured frames at this rate
  - Result: video plays at 5x speed in standard players

### Q4: Directory Management

**Question**: Where should timelapse videos be saved and how to handle directory creation?

**Decision**: Use platformdirs to get application data directory, create `timelapses/` subdirectory automatically
- **Rationale**:
  - Consistent with existing codebase patterns (snapshots directory)
  - Cross-platform support via platformdirs
  - Automatic directory creation ensures user doesn't need to set up directories
- **Implementation Approach**: 
  - Use `platformdirs.user_data_dir('pick-a-zoo')` / `timelapses`
  - Create directory if it doesn't exist on first timelapse creation
  - Handle permission errors gracefully

## Dependencies

### New Dependencies Required

- **imageio-ffmpeg**: Video encoding library (wrapper around FFmpeg)
  - **Version**: Latest stable (>=2.x)
  - **Purpose**: Encode frames into MP4 video files
  - **License**: BSD-2-Clause (compatible)
  - **Size Impact**: Small (wrapper library, FFmpeg must be installed separately)

### Existing Dependencies Used

- **ffpyplayer**: Frame extraction (already in use)
- **numpy**: Frame data manipulation (already in use)
- **PyQt6**: GUI button interface (already in use)
- **platformdirs**: Directory path management (already in use)
- **loguru**: Structured logging (already in use)

## Technical Decisions Summary

1. **Video Encoding**: Use imageio-ffmpeg with MP4/H.264 codec
2. **Frame Capture**: Capture all frames from VideoPlayer, encode at 5x frame rate
3. **File Format**: MP4 with timestamp-based naming
4. **Directory**: Use platformdirs for cross-platform timelapses directory
5. **Speed Implementation**: Encode at 5x source frame rate (e.g., 30fps → 150fps)

## Open Questions Resolved

- ✅ Video encoding library: imageio-ffmpeg selected
- ✅ Frame capture strategy: Capture all frames, encode at 5x rate
- ✅ File format: MP4/H.264
- ✅ Directory management: platformdirs with auto-creation
- ✅ Speed calculation: 5x frame rate encoding

## Next Steps

Proceed to Phase 1: Design & Contracts with resolved technical decisions.

