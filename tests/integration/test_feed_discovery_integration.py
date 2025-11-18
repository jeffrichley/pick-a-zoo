"""Integration tests for feed discovery functionality."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pick_a_zoo.core.feed_discovery import URLType, detect_url_type
from pick_a_zoo.core.feed_manager import load_feeds, resolve_duplicate_name, save_feeds
from pick_a_zoo.core.models import Feed


@pytest.mark.integration
@patch("pick_a_zoo.core.feed_discovery.httpx.Client")
def test_end_to_end_direct_stream_feed_addition(mock_client_class, tmp_path: Path):
    """Test end-to-end direct stream feed addition."""
    from pick_a_zoo.core.feed_discovery import validate_url_accessibility

    # Mock URL detection and validation
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "video/mp4"}
    mock_response.history = []

    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.head.return_value = mock_response
    mock_client_class.return_value = mock_client

    # Test URL detection
    url = "https://example.com/stream.mp4"
    url_type = detect_url_type(url)
    assert url_type == URLType.DIRECT_STREAM

    # Test URL validation
    validation_result = validate_url_accessibility(url)
    assert validation_result.is_accessible is True

    # Test feed creation and saving
    config_file = tmp_path / "feeds.yaml"
    with patch("pick_a_zoo.core.feed_manager.get_config_path", return_value=config_file):
        feed = Feed(name="Test Cam", url=url)
        existing_feeds = load_feeds()
        resolved_name = resolve_duplicate_name(feed.name, existing_feeds)
        feed.name = resolved_name
        existing_feeds.append(feed)
        save_feeds(existing_feeds)

        # Verify feed was saved
        loaded_feeds = load_feeds()
        assert len(loaded_feeds) == 1
        assert loaded_feeds[0].name == "Test Cam"
        assert str(loaded_feeds[0].url) == url


@pytest.mark.integration
def test_duplicate_name_resolution_integration(tmp_path: Path):
    """Test duplicate name resolution integration."""
<<<<<<< HEAD
=======

>>>>>>> 648d97dbbc44e1d48c563b18e2efe2512871323f
    config_file = tmp_path / "feeds.yaml"
    with patch("pick_a_zoo.core.feed_manager.get_config_path", return_value=config_file):
        # Create first feed
        feed1 = Feed(name="Panda Cam", url="https://example.com/1")
        existing_feeds = []
        resolved_name1 = resolve_duplicate_name(feed1.name, existing_feeds)
        feed1.name = resolved_name1
        existing_feeds.append(feed1)
        save_feeds(existing_feeds)

        # Try to add duplicate name
        feed2 = Feed(name="Panda Cam", url="https://example.com/2")
        existing_feeds = load_feeds()
        resolved_name2 = resolve_duplicate_name(feed2.name, existing_feeds)
        feed2.name = resolved_name2
        existing_feeds.append(feed2)
        save_feeds(existing_feeds)

        # Verify both feeds exist with resolved names
        loaded_feeds = load_feeds()
        assert len(loaded_feeds) == 2
        assert loaded_feeds[0].name == "Panda Cam"
        assert loaded_feeds[1].name == "Panda Cam (2)"


@pytest.mark.integration
@patch("pick_a_zoo.core.feed_discovery.httpx.Client")
def test_url_validation_integration(mock_client_class):
    """Test URL validation integration."""
    from pick_a_zoo.core.feed_discovery import validate_url_accessibility

    # Test accessible URL
    mock_response_ok = Mock()
    mock_response_ok.status_code = 200
    mock_response_ok.headers = {"Content-Type": "video/mp4"}
    mock_response_ok.history = []

    # Test inaccessible URL
    mock_response_404 = Mock()
    mock_response_404.status_code = 404
    mock_response_404.headers = {"Content-Type": "text/html"}
    mock_response_404.history = []

    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.head.side_effect = [mock_response_ok, mock_response_404]
    mock_client_class.return_value = mock_client

    # Test accessible URL
    result1 = validate_url_accessibility("https://example.com/stream.mp4")
    assert result1.is_accessible is True
    assert result1.status_code == 200

    # Test inaccessible URL
    result2 = validate_url_accessibility("https://example.com/notfound.mp4")
    assert result2.is_accessible is False
    assert result2.status_code == 404
