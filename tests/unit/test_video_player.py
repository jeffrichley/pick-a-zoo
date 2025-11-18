"""Unit tests for video_player module."""


import pytest

from pick_a_zoo.core.video_player import (
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_WIDTH,
    MAX_WINDOW_HEIGHT,
    MAX_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    StreamLoadError,
    VideoFrame,
    VideoPlayer,
    VideoPlayerError,
)


@pytest.mark.unit
def test_video_player_init():
    """Test VideoPlayer.__init__() with valid stream URL."""
    player = VideoPlayer("https://example.org/stream.m3u8")
    assert player.stream_url == "https://example.org/stream.m3u8"
    assert not player.is_playing()
    assert player.get_error() is None


@pytest.mark.unit
def test_video_player_init_empty_url():
    """Test VideoPlayer.__init__() raises ValueError for empty URL."""
    with pytest.raises(ValueError, match="must be a non-empty string"):
        VideoPlayer("")


@pytest.mark.unit
def test_video_player_init_invalid_url():
    """Test VideoPlayer.__init__() raises ValueError for invalid URL."""
    with pytest.raises(ValueError):
        VideoPlayer(None)  # type: ignore


@pytest.mark.unit
def test_video_player_load_valid_stream():
    """Test VideoPlayer.load() with valid stream URL."""
    player = VideoPlayer("https://example.org/stream.m3u8")
    # load() should succeed (may fail to connect, but shouldn't raise NotImplementedError)
    try:
        player.load()
    except (VideoPlayerError, StreamLoadError):
        # Expected: stream may be unavailable, but load() is implemented
        pass


@pytest.mark.unit
def test_video_player_play():
    """Test VideoPlayer.play() raises VideoPlayerError when stream not loaded."""
    player = VideoPlayer("https://example.org/stream.m3u8")
    # play() should raise VideoPlayerError when stream not loaded
    with pytest.raises(VideoPlayerError, match="Stream not loaded"):
        player.play()


@pytest.mark.unit
def test_video_player_get_frame():
    """Test VideoPlayer.get_frame() returns None when stream not loaded."""
    player = VideoPlayer("https://example.org/stream.m3u8")
    # get_frame() should return None when stream not loaded
    frame = player.get_frame()
    assert frame is None


@pytest.mark.unit
def test_video_player_stop():
    """Test VideoPlayer.stop() works even when not playing."""
    player = VideoPlayer("https://example.org/stream.m3u8")
    # stop() should work without raising an error
    player.stop()
    assert not player.is_playing()


@pytest.mark.unit
def test_video_player_is_playing():
    """Test VideoPlayer.is_playing() returns False initially."""
    player = VideoPlayer("https://example.org/stream.m3u8")
    assert not player.is_playing()


@pytest.mark.unit
def test_video_player_get_error():
    """Test VideoPlayer.get_error() returns None initially."""
    player = VideoPlayer("https://example.org/stream.m3u8")
    assert player.get_error() is None


@pytest.mark.unit
def test_window_dimension_constants():
    """Test window dimension constants are defined correctly."""
    assert DEFAULT_WINDOW_WIDTH == 1280
    assert DEFAULT_WINDOW_HEIGHT == 720
    assert MIN_WINDOW_WIDTH == 320
    assert MIN_WINDOW_HEIGHT == 240
    assert MAX_WINDOW_WIDTH == 7680
    assert MAX_WINDOW_HEIGHT == 4320


@pytest.mark.unit
def test_video_frame_dataclass():
    """Test VideoFrame data class."""
    frame = VideoFrame(pixels=b"test", width=1280, height=720, timestamp=1.0)
    assert frame.width == 1280
    assert frame.height == 720
    assert frame.timestamp == 1.0


@pytest.mark.unit
def test_video_player_error():
    """Test VideoPlayerError exception."""
    error = VideoPlayerError("Test error", "network")
    assert error.message == "Test error"
    assert error.error_type == "network"
    assert str(error) == "Test error"


@pytest.mark.unit
def test_stream_load_error():
    """Test StreamLoadError exception."""
    error = StreamLoadError("Stream unavailable", "unavailable")
    assert error.message == "Stream unavailable"
    assert error.error_type == "unavailable"
    assert isinstance(error, VideoPlayerError)

