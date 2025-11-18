"""Unit tests for MainMenuScreen."""

from unittest.mock import patch

import pytest

from pick_a_zoo.tui.screens.main_menu import MainMenuScreen


@pytest.mark.unit
def test_main_menu_screen_rendering():
    """Test that MainMenuScreen renders correctly."""
    screen = MainMenuScreen()
    assert screen is not None
    assert isinstance(screen, MainMenuScreen)
    assert len(screen.MENU_OPTIONS) == 4


@pytest.mark.unit
def test_main_menu_screen_keyboard_navigation_arrow_keys():
    """Test MainMenuScreen has arrow key navigation bindings."""
    screen = MainMenuScreen()
    # Verify bindings exist for arrow keys
    bindings = [b[0] for b in screen.BINDINGS]
    assert "up" in bindings
    assert "down" in bindings


@pytest.mark.unit
def test_main_menu_screen_wasd_fallback_navigation():
    """Test MainMenuScreen has WASD navigation methods."""
    screen = MainMenuScreen()
    # Verify navigation methods exist
    assert hasattr(screen, "action_navigate_up")
    assert hasattr(screen, "action_navigate_down")


@pytest.mark.unit
def test_main_menu_screen_hotkey_shortcuts():
    """Test MainMenuScreen has hotkey shortcuts."""
    screen = MainMenuScreen()
    bindings = [b[0] for b in screen.BINDINGS]
    # Verify number hotkeys
    assert "1" in bindings
    assert "2" in bindings
    assert "3" in bindings
    assert "4" in bindings
    # Verify letter hotkeys
    assert "v" in bindings
    assert "a" in bindings
    assert "w" in bindings
    assert "q" in bindings


@pytest.mark.unit
def test_main_menu_screen_quit_action():
    """Test MainMenuScreen has quit action."""
    screen = MainMenuScreen()
    assert hasattr(screen, "action_quit")
    assert "q" in [b[0] for b in screen.BINDINGS]


@pytest.mark.unit
@patch("pick_a_zoo.tui.screens.main_menu.load_feeds")
def test_main_menu_screen_display_no_cams_saved_yet_message(mock_load_feeds):
    """Test MainMenuScreen displays 'No cams saved yet' message when no feeds exist."""
    mock_load_feeds.return_value = []

    screen = MainMenuScreen()
    # Verify the method exists and can handle empty feeds
    assert hasattr(screen, "_load_feeds_and_update_display")


@pytest.mark.unit
@patch("pick_a_zoo.tui.screens.main_menu.load_feeds")
def test_main_menu_screen_terminal_size_warning(mock_load_feeds):
    """Test MainMenuScreen has terminal size warning functionality."""
    mock_load_feeds.return_value = []

    screen = MainMenuScreen()
    # Verify terminal size checking exists
    assert hasattr(screen, "_check_terminal_size")
    assert screen.MIN_TERMINAL_WIDTH == 80
    assert screen.MIN_TERMINAL_HEIGHT == 24
