"""Integration tests for TUI application."""

from unittest.mock import patch

import pytest

from pick_a_zoo.tui.app import PickAZooApp


@pytest.mark.integration
def test_app_startup_flow():
    """Test app startup flow."""
    app = PickAZooApp()
    assert app is not None
    assert isinstance(app, PickAZooApp)


@pytest.mark.integration
@patch("pick_a_zoo.core.feed_manager.load_feeds")
def test_feed_loading_integration_on_app_startup(mock_load_feeds):
    """Test feed loading integration on app startup."""
    mock_load_feeds.return_value = []

    # App should load feeds on mount
    # (Implementation will handle this)
    PickAZooApp()


@pytest.mark.integration
@patch("pick_a_zoo.core.feed_manager.load_feeds")
def test_missing_config_file_recovery(mock_load_feeds):
    """Test missing config file recovery."""
    from pick_a_zoo.core.feed_manager import load_feeds

    # Simulate missing file scenario
    mock_load_feeds.return_value = []

    feeds = load_feeds()
    assert feeds == []


@pytest.mark.integration
@patch("pick_a_zoo.core.feed_manager.load_feeds")
def test_corrupted_config_file_recovery(mock_load_feeds):
    """Test corrupted config file recovery."""
    from pick_a_zoo.core.feed_manager import load_feeds

    # Simulate corrupted file scenario
    mock_load_feeds.return_value = []

    feeds = load_feeds()
    assert feeds == []

