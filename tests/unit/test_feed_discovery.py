"""Unit tests for feed_discovery module."""

from unittest.mock import Mock, patch

import httpx
import pytest

from pick_a_zoo.core.feed_discovery import (
    HTMLParseError,
    StreamCandidate,
    URLType,
    URLValidationError,
    URLValidationResult,
    detect_url_type,
    extract_streams_from_html,
    validate_url_accessibility,
)


@pytest.mark.unit
def test_detect_url_type_with_m3u8_direct_stream():
    """Test detect_url_type() with direct stream URL (.m3u8)."""
    url = "https://example.com/stream.m3u8"
    result = detect_url_type(url)
    assert result == URLType.DIRECT_STREAM


@pytest.mark.unit
def test_detect_url_type_with_mp4_direct_stream():
    """Test detect_url_type() with direct stream URL (.mp4)."""
    url = "https://example.com/video.mp4"
    result = detect_url_type(url)
    assert result == URLType.DIRECT_STREAM


@pytest.mark.unit
def test_detect_url_type_with_webm_direct_stream():
    """Test detect_url_type() with direct stream URL (.webm)."""
    url = "https://example.com/video.webm"
    result = detect_url_type(url)
    assert result == URLType.DIRECT_STREAM


@pytest.mark.unit
def test_detect_url_type_with_rtsp_direct_stream():
    """Test detect_url_type() with direct stream URL (rtsp://)."""
    url = "rtsp://example.com/stream"
    result = detect_url_type(url)
    assert result == URLType.DIRECT_STREAM


@pytest.mark.unit
@patch("pick_a_zoo.core.feed_discovery.httpx.Client")
def test_detect_url_type_with_html_page_via_content_type(mock_client_class):
    """Test detect_url_type() with HTML page URL (via Content-Type)."""
    # Mock HTTP response with HTML Content-Type
    mock_response = Mock()
    mock_response.headers = {"Content-Type": "text/html; charset=utf-8"}
    mock_response.history = []

    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.head.return_value = mock_response
    mock_client_class.return_value = mock_client

    url = "https://example.com/page.html"
    result = detect_url_type(url)
    assert result == URLType.HTML_PAGE


@pytest.mark.unit
@patch("pick_a_zoo.core.feed_discovery.httpx.Client")
def test_detect_url_type_with_redirect_handling(mock_client_class):
    """Test detect_url_type() with redirect handling."""
    # Mock HTTP response with redirects (but less than 5)
    mock_response = Mock()
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.history = [Mock(), Mock()]  # 2 redirects

    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.head.return_value = mock_response
    mock_client_class.return_value = mock_client

    url = "https://example.com/redirect"
    result = detect_url_type(url)
    assert result == URLType.HTML_PAGE


@pytest.mark.unit
@patch("pick_a_zoo.core.feed_discovery.httpx.Client")
def test_detect_url_type_error_handling_network_error(mock_client_class):
    """Test detect_url_type() error handling (network error)."""
    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.head.side_effect = httpx.NetworkError("Connection failed")
    mock_client_class.return_value = mock_client

    # Use a URL that doesn't match direct stream patterns to force HTTP request
    url = "https://example.com/page"
    with pytest.raises(URLValidationError) as exc_info:
        detect_url_type(url)
    assert "Network error" in str(exc_info.value)


@pytest.mark.unit
@patch("pick_a_zoo.core.feed_discovery.httpx.Client")
def test_validate_url_accessibility_with_accessible_url(mock_client_class):
    """Test validate_url_accessibility() with accessible URL."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "video/mp4"}
    mock_response.history = []

    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.head.return_value = mock_response
    mock_client_class.return_value = mock_client

    url = "https://example.com/stream.mp4"
    result = validate_url_accessibility(url)
    assert isinstance(result, URLValidationResult)
    assert result.is_accessible is True
    assert result.status_code == 200
    assert result.error_message is None
    assert result.content_type == "video/mp4"


@pytest.mark.unit
@patch("pick_a_zoo.core.feed_discovery.httpx.Client")
def test_validate_url_accessibility_with_inaccessible_url_404(mock_client_class):
    """Test validate_url_accessibility() with inaccessible URL (404)."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.headers = {"Content-Type": "text/html"}
    mock_response.history = []

    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.head.return_value = mock_response
    mock_client_class.return_value = mock_client

    url = "https://example.com/notfound.mp4"
    result = validate_url_accessibility(url)
    assert isinstance(result, URLValidationResult)
    assert result.is_accessible is False
    assert result.status_code == 404
    assert result.error_message == "HTTP 404"


@pytest.mark.unit
@patch("pick_a_zoo.core.feed_discovery.httpx.Client")
def test_validate_url_accessibility_with_timeout_scenario(mock_client_class):
    """Test validate_url_accessibility() with timeout scenario."""
    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.head.side_effect = httpx.TimeoutException("Request timed out")
    mock_client_class.return_value = mock_client

    url = "https://example.com/slow.mp4"
    with pytest.raises(URLValidationError) as exc_info:
        validate_url_accessibility(url, timeout=5.0)
    assert "Timeout" in str(exc_info.value)
    assert "5.0" in str(exc_info.value.user_message)


@pytest.mark.unit
@patch("pick_a_zoo.core.feed_discovery.httpx.Client")
def test_validate_url_accessibility_with_network_error(mock_client_class):
    """Test validate_url_accessibility() with network error."""
    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.head.side_effect = httpx.ConnectError("Connection refused")
    mock_client_class.return_value = mock_client

    url = "https://example.com/unreachable.mp4"
    with pytest.raises(URLValidationError) as exc_info:
        validate_url_accessibility(url)
    assert "Connection error" in str(exc_info.value)


@pytest.mark.unit
@patch("pick_a_zoo.core.feed_discovery.httpx.Client")
def test_validate_url_accessibility_with_redirect_handling(mock_client_class):
    """Test validate_url_accessibility() with redirect handling."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "video/mp4"}
    mock_response.history = [Mock(), Mock()]  # 2 redirects

    mock_client = Mock()
    mock_client.__enter__ = Mock(return_value=mock_client)
    mock_client.__exit__ = Mock(return_value=False)
    mock_client.head.return_value = mock_response
    mock_client_class.return_value = mock_client

    url = "https://example.com/redirect.mp4"
    result = validate_url_accessibility(url)
    assert result.is_accessible is True
    assert result.status_code == 200

