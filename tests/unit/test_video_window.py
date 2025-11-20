"""Unit tests for video_window module."""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_pyqt6():
    """Create a mock PyQt6 module structure and inject into sys.modules."""

    # Create mock classes that can be instantiated without spec issues
    def make_mock_class(name):
        # Use MagicMock - it will return new MagicMock instances when called
        # Configure side_effect to return a new instance, ignoring args to avoid spec issues
        mock_class = MagicMock()
        mock_class.__name__ = name
        # Default behavior: return a new MagicMock when instantiated
        mock_class.side_effect = lambda *args, **kwargs: MagicMock()
        return mock_class

    mock_qt_widgets = Mock()
    mock_qt_widgets.QMainWindow = make_mock_class("QMainWindow")
    mock_qt_widgets.QWidget = make_mock_class("QWidget")
    mock_qt_widgets.QLabel = make_mock_class("QLabel")
    mock_qt_widgets.QVBoxLayout = make_mock_class("QVBoxLayout")
    mock_qt_widgets.QPushButton = make_mock_class("QPushButton")

    mock_qt_core = Mock()
    mock_qt_core.Qt = Mock()
    mock_qt_core.Qt.AlignmentFlag = Mock(AlignCenter=Mock())
    mock_qt_core.QTimer = make_mock_class("QTimer")

    mock_pyqt6 = Mock()
    mock_pyqt6.QtWidgets = mock_qt_widgets
    mock_pyqt6.QtCore = mock_qt_core

    # Inject into sys.modules so imports work
    with patch.dict(
        sys.modules,
        {
            "PyQt6": mock_pyqt6,
            "PyQt6.QtWidgets": mock_qt_widgets,
            "PyQt6.QtCore": mock_qt_core,
        },
    ):
        yield mock_pyqt6


@pytest.mark.unit
def test_video_window_init(mock_pyqt6):
    """Test VideoWindow.__init__()."""
    from pick_a_zoo.gui.video_window import VideoWindow

    mock_window = MagicMock()
    # Configure QMainWindow to return our mock_window when instantiated
    mock_pyqt6.QtWidgets.QMainWindow.side_effect = lambda *args, **kwargs: mock_window

    window = VideoWindow("Panda Cam", "https://example.org/panda.m3u8", 1280, 720)
    assert window.feed_name == "Panda Cam"
    assert window.stream_url == "https://example.org/panda.m3u8"


@pytest.mark.unit
def test_video_window_show(mock_pyqt6):
    """Test VideoWindow.show()."""
    from pick_a_zoo.gui.video_window import VideoWindow

    mock_window = MagicMock()
    # Configure QMainWindow to return our mock_window when instantiated
    mock_pyqt6.QtWidgets.QMainWindow.side_effect = lambda *args, **kwargs: mock_window

    with patch("pick_a_zoo.gui.video_window.VideoPlayer") as mock_player_class:
        mock_player = MagicMock()
        mock_player_class.return_value = mock_player

        window = VideoWindow("Panda Cam", "https://example.org/panda.m3u8", 1280, 720)
        window.show()

        # Verify VideoPlayer was created and started
        mock_player_class.assert_called_once_with("https://example.org/panda.m3u8")
        mock_player.load.assert_called_once()
        mock_player.play.assert_called_once()
        # Verify window.show() was called on the mock window
        assert window._window is mock_window
        mock_window.show.assert_called_once()


@pytest.mark.unit
def test_video_window_timelapse_button_creation(mock_pyqt6):
    """Test VideoWindow creates timelapse button."""
    from pick_a_zoo.gui.video_window import VideoWindow

    # Use default mock behavior - QMainWindow will return a new MagicMock
    window = VideoWindow("Panda Cam", "https://example.org/panda.m3u8", 1280, 720)

    # Verify button was created and added to layout
    assert hasattr(window, "timelapse_button")
    mock_pyqt6.QtWidgets.QPushButton.assert_called()


@pytest.mark.unit
def test_video_window_timelapse_button_clicked(mock_pyqt6):
    """Test VideoWindow._on_timelapse_button_clicked() toggles recording."""
    from pick_a_zoo.gui.video_window import VideoWindow

    # Use default mock behavior - QMainWindow will return a new MagicMock
    with patch("pick_a_zoo.core.timelapse_encoder.TimelapseEncoder") as mock_encoder_class:
        mock_encoder = MagicMock()
        mock_encoder_class.return_value = mock_encoder

        window = VideoWindow("Panda Cam", "https://example.org/panda.m3u8", 1280, 720)

        # Mock player as playing
        window._player = MagicMock()
        window._player.is_playing.return_value = True

        # First click should start recording
        window._on_timelapse_button_clicked()
        mock_encoder.start_recording.assert_called_once_with("Panda Cam", source_fps=30.0)

        # Second click should stop recording
        mock_encoder.is_recording.return_value = True
        window._on_timelapse_button_clicked()
        mock_encoder.stop_recording.assert_called_once()
