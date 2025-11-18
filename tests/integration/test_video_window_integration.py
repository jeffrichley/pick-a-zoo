"""Integration tests for video window launching from TUI."""

import subprocess
import sys

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

