"""Unit tests for video_window module."""

from unittest.mock import MagicMock, patch

import pytest

from pick_a_zoo.gui.video_window import VideoWindow


@pytest.mark.unit
def test_video_window_init():
    """Test VideoWindow.__init__()."""
    # Mock PyQt6 imports inside the __init__ method
    with patch("PyQt6.QtWidgets.QMainWindow"), patch(
        "PyQt6.QtWidgets.QWidget"
    ), patch("PyQt6.QtWidgets.QLabel"), patch(
        "PyQt6.QtWidgets.QVBoxLayout"
    ), patch("PyQt6.QtCore.Qt"):
        window = VideoWindow("Panda Cam", "https://example.org/panda.m3u8", 1280, 720)
        assert window.feed_name == "Panda Cam"
        assert window.stream_url == "https://example.org/panda.m3u8"


@pytest.mark.unit
def test_video_window_show():
    """Test VideoWindow.show()."""
    # Mock PyQt6 imports inside the __init__ method and VideoPlayer
    with patch("PyQt6.QtWidgets.QMainWindow") as mock_qmainwindow, patch(
        "PyQt6.QtWidgets.QWidget"
    ), patch("PyQt6.QtWidgets.QLabel"), patch(
        "PyQt6.QtWidgets.QVBoxLayout"
    ), patch("PyQt6.QtCore.Qt"), patch(
        "PyQt6.QtCore.QTimer"
    ), patch(
        "pick_a_zoo.gui.video_window.VideoPlayer"
    ) as mock_player_class:
        mock_window = MagicMock()
        mock_qmainwindow.return_value = mock_window
        mock_player = MagicMock()
        mock_player_class.return_value = mock_player

        window = VideoWindow("Panda Cam", "https://example.org/panda.m3u8", 1280, 720)
        window.show()

        # Verify VideoPlayer was created and started
        mock_player_class.assert_called_once_with("https://example.org/panda.m3u8")
        mock_player.load.assert_called_once()
        mock_player.play.assert_called_once()
        # Verify window.show() was called
        mock_window.show.assert_called_once()

