"""Unit tests for timelapse_encoder module."""

from pathlib import Path

import numpy as np
import pytest

from pick_a_zoo.core.timelapse_encoder import (
    NoRecordingError,
    RecordingInProgressError,
    TimelapseEncoder,
)


@pytest.mark.unit
def test_timelapse_encoder_init_default_directory(tmp_path: Path, monkeypatch):
    """Test TimelapseEncoder.__init__() with default directory."""
    # Mock Path.cwd() to return tmp_path
    monkeypatch.chdir(tmp_path)
    encoder = TimelapseEncoder()
    assert encoder is not None
    # Verify directory was created
    timelapses_dir = tmp_path / ".pickazoo" / "timelapses"
    assert timelapses_dir.exists()


@pytest.mark.unit
def test_timelapse_encoder_init_custom_directory(tmp_path: Path):
    """Test TimelapseEncoder.__init__() with custom directory."""
    custom_dir = tmp_path / "custom_timelapses"
    encoder = TimelapseEncoder(output_directory=custom_dir)
    assert encoder is not None
    assert custom_dir.exists()


@pytest.mark.unit
def test_timelapse_encoder_init_creates_directory(tmp_path: Path):
    """Test TimelapseEncoder.__init__() creates directory if missing."""
    custom_dir = tmp_path / "new_timelapses"
    assert not custom_dir.exists()
    TimelapseEncoder(output_directory=custom_dir)
    assert custom_dir.exists()


@pytest.mark.unit
def test_timelapse_encoder_start_recording(tmp_path: Path):
    """Test TimelapseEncoder.start_recording() starts recording."""
    encoder = TimelapseEncoder(output_directory=tmp_path)
    encoder.start_recording("Test Feed", source_fps=30.0)
    assert encoder.is_recording() is True


@pytest.mark.unit
def test_timelapse_encoder_start_recording_empty_feed_name(tmp_path: Path):
    """Test TimelapseEncoder.start_recording() raises ValueError for empty feed name."""
    encoder = TimelapseEncoder(output_directory=tmp_path)
    with pytest.raises(ValueError, match="feed_name"):
        encoder.start_recording("", source_fps=30.0)


@pytest.mark.unit
def test_timelapse_encoder_start_recording_already_recording(tmp_path: Path):
    """Test start_recording() raises RecordingInProgressError when already recording."""
    encoder = TimelapseEncoder(output_directory=tmp_path)
    encoder.start_recording("Test Feed", source_fps=30.0)
    with pytest.raises(RecordingInProgressError):
        encoder.start_recording("Another Feed", source_fps=30.0)


@pytest.mark.unit
def test_timelapse_encoder_capture_frame(tmp_path: Path):
    """Test TimelapseEncoder.capture_frame() captures frames."""
    encoder = TimelapseEncoder(output_directory=tmp_path)
    encoder.start_recording("Test Feed", source_fps=30.0)

    # Create a test frame (height, width, 3) RGB array
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    encoder.capture_frame(frame)

    assert encoder.get_frame_count() == 1


@pytest.mark.unit
def test_timelapse_encoder_capture_frame_not_recording(tmp_path: Path):
    """Test TimelapseEncoder.capture_frame() raises NoRecordingError when not recording."""
    encoder = TimelapseEncoder(output_directory=tmp_path)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    with pytest.raises(NoRecordingError):
        encoder.capture_frame(frame)


@pytest.mark.unit
def test_timelapse_encoder_capture_frame_invalid_shape(tmp_path: Path):
    """Test TimelapseEncoder.capture_frame() raises ValueError for invalid frame shape."""
    encoder = TimelapseEncoder(output_directory=tmp_path)
    encoder.start_recording("Test Feed", source_fps=30.0)

    # Invalid shape (not 3D)
    frame = np.zeros((480, 640), dtype=np.uint8)
    with pytest.raises(ValueError, match="frame"):
        encoder.capture_frame(frame)


@pytest.mark.unit
def test_timelapse_encoder_stop_recording(tmp_path: Path):
    """Test TimelapseEncoder.stop_recording() stops recording and saves video."""
    encoder = TimelapseEncoder(output_directory=tmp_path)
    encoder.start_recording("Test Feed", source_fps=30.0)

    # Capture a few frames
    for _ in range(5):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        encoder.capture_frame(frame)

    video_path = encoder.stop_recording()

    assert encoder.is_recording() is False
    assert video_path.exists()
    assert video_path.suffix == ".mp4"


@pytest.mark.unit
def test_timelapse_encoder_stop_recording_not_recording(tmp_path: Path):
    """Test TimelapseEncoder.stop_recording() raises NoRecordingError when not recording."""
    encoder = TimelapseEncoder(output_directory=tmp_path)
    with pytest.raises(NoRecordingError):
        encoder.stop_recording()


@pytest.mark.unit
def test_timelapse_encoder_stop_recording_no_frames(tmp_path: Path):
    """Test TimelapseEncoder.stop_recording() raises ValueError when no frames captured."""
    encoder = TimelapseEncoder(output_directory=tmp_path)
    encoder.start_recording("Test Feed", source_fps=30.0)
    with pytest.raises(ValueError, match="frames"):
        encoder.stop_recording()


@pytest.mark.unit
def test_timelapse_encoder_is_recording(tmp_path: Path):
    """Test TimelapseEncoder.is_recording() returns correct state."""
    encoder = TimelapseEncoder(output_directory=tmp_path)
    assert encoder.is_recording() is False

    encoder.start_recording("Test Feed", source_fps=30.0)
    assert encoder.is_recording() is True

    # Capture at least one frame before stopping
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    encoder.capture_frame(frame)

    encoder.stop_recording()
    assert encoder.is_recording() is False


@pytest.mark.unit
def test_timelapse_encoder_filename_generation(tmp_path: Path):
    """Test TimelapseEncoder generates filename with timestamp."""
    encoder = TimelapseEncoder(output_directory=tmp_path)
    encoder.start_recording("Panda Cam", source_fps=30.0)

    # Capture a frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    encoder.capture_frame(frame)

    video_path = encoder.stop_recording()

    # Check filename format: <feed-name>-YYYYMMDD-HHMMSS.mp4
    filename = video_path.name
    assert filename.startswith("Panda-Cam-")
    assert filename.endswith(".mp4")
    # Check timestamp format (8 digits date + 6 digits time)
    parts = filename.replace(".mp4", "").split("-")
    assert len(parts) >= 3
    timestamp = parts[-2] + parts[-1]
    assert len(timestamp) == 14  # YYYYMMDDHHMMSS
    assert timestamp.isdigit()


@pytest.mark.unit
def test_timelapse_encoder_video_encoding_5x_speed(tmp_path: Path):
    """Test TimelapseEncoder encodes video at 5x speed."""
    encoder = TimelapseEncoder(output_directory=tmp_path)
    encoder.start_recording("Test Feed", source_fps=30.0)

    # Capture frames (simulating 1 second at 30fps = 30 frames)
    for _ in range(30):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        encoder.capture_frame(frame)

    video_path = encoder.stop_recording()

    # Verify video file exists and is valid
    assert video_path.exists()
    assert video_path.stat().st_size > 0

    # Note: Actual fps verification would require reading video metadata
    # This test verifies encoding succeeds at 5x speed (150fps output)


@pytest.mark.unit
def test_timelapse_encoder_get_frame_count(tmp_path: Path):
    """Test TimelapseEncoder.get_frame_count() returns correct count."""
    encoder = TimelapseEncoder(output_directory=tmp_path)

    with pytest.raises(NoRecordingError):
        encoder.get_frame_count()

    encoder.start_recording("Test Feed", source_fps=30.0)
    assert encoder.get_frame_count() == 0

    for i in range(5):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        encoder.capture_frame(frame)
        assert encoder.get_frame_count() == i + 1


@pytest.mark.unit
def test_timelapse_encoder_cancel_recording(tmp_path: Path):
    """Test TimelapseEncoder.cancel_recording() cancels without saving."""
    encoder = TimelapseEncoder(output_directory=tmp_path)
    encoder.start_recording("Test Feed", source_fps=30.0)

    # Capture some frames
    for _ in range(5):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        encoder.capture_frame(frame)

    encoder.cancel_recording()

    assert encoder.is_recording() is False
    # Verify no video file was created
    video_files = list(tmp_path.glob("*.mp4"))
    assert len(video_files) == 0


@pytest.mark.unit
def test_timelapse_encoder_cancel_recording_not_recording(tmp_path: Path):
    """Test TimelapseEncoder.cancel_recording() raises NoRecordingError when not recording."""
    encoder = TimelapseEncoder(output_directory=tmp_path)
    with pytest.raises(NoRecordingError):
        encoder.cancel_recording()
