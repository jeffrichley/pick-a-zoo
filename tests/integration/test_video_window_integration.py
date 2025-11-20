"""Integration tests for video window launching from TUI."""

import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.integration
@pytest.mark.skip(reason="GUI test requires display and may timeout")
def test_video_window_launching_from_tui():
    """Integration test for video window launching via player_launcher subprocess."""
    # Test that player_launcher can be invoked as a module
    # This verifies the subprocess launch mechanism works
    # Note: This test is skipped because it launches a GUI window which may timeout
    # or require a display server
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pick_a_zoo.gui.player_launcher",
            "Test Feed",
            "https://example.org/test.m3u8",
            "1280",
            "720",
        ],
        capture_output=True,
        timeout=5,  # Should fail quickly if stream unavailable
    )
    # Should exit with non-zero (stream unavailable) but not crash
    assert result.returncode != 0  # Expected: stream unavailable, not a crash


@pytest.mark.integration
def test_timelapse_creation_workflow(tmp_path: Path):
    """Integration test for timelapse creation workflow."""

    import numpy as np

    from pick_a_zoo.core.timelapse_encoder import TimelapseEncoder

    # Create encoder
    encoder = TimelapseEncoder(output_directory=tmp_path)

    # Start recording
    encoder.start_recording("Test Feed", source_fps=30.0)
    assert encoder.is_recording() is True

    # Simulate capturing frames from video player
    for i in range(30):  # 1 second at 30fps
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add some variation to frames
        frame[:, :, 0] = i % 255
        encoder.capture_frame(frame)

    assert encoder.get_frame_count() == 30

    # Stop recording and save video
    video_path = encoder.stop_recording()

    # Verify video was created
    assert video_path.exists()
    assert video_path.stat().st_size > 0
    assert encoder.is_recording() is False
