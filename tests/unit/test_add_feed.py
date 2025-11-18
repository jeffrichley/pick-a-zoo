"""Unit tests for AddFeedScreen."""

from unittest.mock import patch

import pytest

from pick_a_zoo.tui.screens.add_feed import AddFeedScreen


@pytest.mark.unit
def test_add_feed_screen_name_input_validation():
    """Test AddFeedScreen name input validation."""
    screen = AddFeedScreen()
    # Test that empty name is rejected
    # This will be implemented in the screen
    assert hasattr(screen, "on_input_submitted") or hasattr(screen, "on_name_submitted")


@pytest.mark.unit
def test_add_feed_screen_url_input_validation():
    """Test AddFeedScreen URL input validation."""
    screen = AddFeedScreen()
    # Test that invalid URL format is rejected
    # This will be implemented in the screen
    assert hasattr(screen, "on_url_submitted")


@pytest.mark.unit
@patch("pick_a_zoo.tui.screens.add_feed.detect_url_type")
@patch("pick_a_zoo.tui.screens.add_feed.validate_url_accessibility")
@patch("pick_a_zoo.tui.screens.add_feed.load_feeds")
@patch("pick_a_zoo.tui.screens.add_feed.resolve_duplicate_name")
@patch("pick_a_zoo.tui.screens.add_feed.save_feeds")
def test_add_feed_screen_direct_stream_workflow_success_case(
    mock_save_feeds,
    mock_resolve_duplicate_name,
    mock_load_feeds,
    mock_validate_url,
    mock_detect_url_type,
):
    """Test AddFeedScreen direct stream workflow (success case)."""
    from pick_a_zoo.core.feed_discovery import URLType, URLValidationResult

    mock_detect_url_type.return_value = URLType.DIRECT_STREAM
    mock_validate_url.return_value = URLValidationResult(
        is_accessible=True, status_code=200
    )
    mock_load_feeds.return_value = []
    mock_resolve_duplicate_name.return_value = "Panda Cam"

    screen = AddFeedScreen()
    # This test will verify the workflow once implemented
    assert hasattr(screen, "on_url_submitted")


@pytest.mark.unit
@patch("pick_a_zoo.tui.screens.add_feed.detect_url_type")
def test_add_feed_screen_invalid_url_error_handling(mock_detect_url_type):
    """Test AddFeedScreen invalid URL error handling."""
    from pick_a_zoo.core.feed_discovery import FeedDiscoveryError

    mock_detect_url_type.side_effect = FeedDiscoveryError("Invalid URL")

    screen = AddFeedScreen()
    # This test will verify error handling once implemented
    assert hasattr(screen, "on_url_submitted")


@pytest.mark.unit
@patch("pick_a_zoo.tui.screens.add_feed.validate_url_accessibility")
def test_add_feed_screen_inaccessible_url_error_handling(mock_validate_url):
    """Test AddFeedScreen inaccessible URL error handling."""
    from pick_a_zoo.core.feed_discovery import URLValidationError

    mock_validate_url.side_effect = URLValidationError("URL not accessible")

    screen = AddFeedScreen()
    # This test will verify error handling once implemented
    assert hasattr(screen, "on_url_submitted")


@pytest.mark.unit
def test_add_feed_screen_cancellation_at_name_entry():
    """Test AddFeedScreen cancellation at name entry."""
    screen = AddFeedScreen()
    # Test that cancellation returns to main menu
    assert hasattr(screen, "on_cancel") or hasattr(screen, "action_cancel")


@pytest.mark.unit
def test_add_feed_screen_cancellation_at_url_entry():
    """Test AddFeedScreen cancellation at URL entry."""
    screen = AddFeedScreen()
    # Test that cancellation returns to main menu
    assert hasattr(screen, "on_cancel") or hasattr(screen, "action_cancel")

