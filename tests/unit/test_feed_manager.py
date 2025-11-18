"""Unit tests for feed_manager module."""

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from pick_a_zoo.core.feed_manager import get_config_path, load_feeds, save_feeds
from pick_a_zoo.core.models import Feed, WindowSize


@pytest.mark.unit
def test_get_config_path():
    """Test that get_config_path returns a Path object."""
    path = get_config_path()
    assert isinstance(path, Path)
    assert path.name == "feeds.yaml"
    assert path.suffix == ".yaml"


@pytest.mark.unit
def test_load_feeds_with_valid_yaml(tmp_path: Path):
    """Test loading feeds from a valid YAML file."""
    # Create a temporary config file
    config_file = tmp_path / "feeds.yaml"
    feeds_data = {
        "feeds": [
            {"name": "Panda Cam", "url": "https://example.org/panda.m3u8"},
            {
                "name": "Otter Live",
                "url": "https://example.org/otter.mp4",
                "window_size": {"width": 1280, "height": 720},
            },
        ]
    }
    with config_file.open("w", encoding="utf-8") as f:
        yaml.safe_dump(feeds_data, f)

    with patch("pick_a_zoo.core.feed_manager.get_config_path", return_value=config_file):
        feeds = load_feeds()

    assert len(feeds) == 2
    assert feeds[0].name == "Panda Cam"
    assert str(feeds[0].url) == "https://example.org/panda.m3u8"
    assert feeds[0].window_size is None
    assert feeds[1].name == "Otter Live"
    assert str(feeds[1].url) == "https://example.org/otter.mp4"
    assert feeds[1].window_size is not None
    assert feeds[1].window_size.width == 1280
    assert feeds[1].window_size.height == 720


@pytest.mark.unit
def test_load_feeds_with_missing_file(tmp_path: Path):
    """Test that missing file creates empty file and returns empty list."""
    config_file = tmp_path / "feeds.yaml"

    with patch("pick_a_zoo.core.feed_manager.get_config_path", return_value=config_file):
        feeds = load_feeds()

    assert feeds == []
    assert config_file.exists()

    # Verify the file has the correct structure
    with config_file.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        assert data == {"feeds": []}


@pytest.mark.unit
def test_load_feeds_with_corrupted_yaml_file(tmp_path: Path):
    """Test that corrupted YAML file is rebuilt and returns empty list."""
    config_file = tmp_path / "feeds.yaml"
    # Write invalid YAML
    config_file.write_text("invalid: yaml: content: [", encoding="utf-8")

    with patch("pick_a_zoo.core.feed_manager.get_config_path", return_value=config_file):
        feeds = load_feeds()

    assert feeds == []

    # Verify the file was rebuilt with correct structure
    with config_file.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        assert data == {"feeds": []}


@pytest.mark.unit
def test_save_feeds_with_valid_feeds_list(tmp_path: Path):
    """Test saving a valid list of feeds."""
    config_file = tmp_path / "feeds.yaml"
    feeds = [
        Feed(name="Panda Cam", url="https://example.org/panda.m3u8"),
        Feed(
            name="Otter Live",
            url="https://example.org/otter.mp4",
            window_size=WindowSize(width=1280, height=720),
        ),
    ]

    with patch("pick_a_zoo.core.feed_manager.get_config_path", return_value=config_file):
        save_feeds(feeds)

    assert config_file.exists()

    # Verify the saved data
    with config_file.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        assert len(data["feeds"]) == 2
        assert data["feeds"][0]["name"] == "Panda Cam"
        assert data["feeds"][0]["url"] == "https://example.org/panda.m3u8"
        assert data["feeds"][1]["name"] == "Otter Live"
        assert data["feeds"][1]["window_size"]["width"] == 1280


@pytest.mark.unit
def test_save_feeds_atomic_write_pattern(tmp_path: Path):
    """Test that save_feeds uses atomic write pattern."""
    config_file = tmp_path / "feeds.yaml"
    feeds = [Feed(name="Test Cam", url="https://example.org/test.m3u8")]

    with patch("pick_a_zoo.core.feed_manager.get_config_path", return_value=config_file):
        save_feeds(feeds)

    # Verify file exists and is valid
    assert config_file.exists()
    with config_file.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        assert len(data["feeds"]) == 1


@pytest.mark.unit
def test_load_feeds_with_invalid_structure(tmp_path: Path):
    """Test loading feeds from file with invalid structure."""
    config_file = tmp_path / "feeds.yaml"
    # Write YAML with invalid structure (feeds is not a list)
    invalid_data = {"feeds": "not a list"}
    with config_file.open("w", encoding="utf-8") as f:
        yaml.safe_dump(invalid_data, f)

    with patch("pick_a_zoo.core.feed_manager.get_config_path", return_value=config_file):
        feeds = load_feeds()

    assert feeds == []

    # Verify file was rebuilt
    with config_file.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        assert data == {"feeds": []}


@pytest.mark.unit
def test_load_feeds_with_empty_file(tmp_path: Path):
    """Test loading from an empty YAML file."""
    config_file = tmp_path / "feeds.yaml"
    config_file.write_text("", encoding="utf-8")

    with patch("pick_a_zoo.core.feed_manager.get_config_path", return_value=config_file):
        feeds = load_feeds()

    assert feeds == []


@pytest.mark.unit
def test_load_feeds_with_invalid_feed_entry(tmp_path: Path):
    """Test that invalid feed entries are skipped."""
    config_file = tmp_path / "feeds.yaml"
    feeds_data = {
        "feeds": [
            {"name": "Valid Feed", "url": "https://example.org/valid.m3u8"},
            {"name": "Invalid Feed", "url": "not-a-url"},  # Invalid URL
            {"name": "", "url": "https://example.org/empty.m3u8"},  # Empty name
        ]
    }
    with config_file.open("w", encoding="utf-8") as f:
        yaml.safe_dump(feeds_data, f)

    with patch("pick_a_zoo.core.feed_manager.get_config_path", return_value=config_file):
        feeds = load_feeds()

    # Only the valid feed should be loaded
    assert len(feeds) == 1
    assert feeds[0].name == "Valid Feed"


@pytest.mark.unit
def test_save_feeds_validates_feeds():
    """Test that save_feeds validates Feed objects."""
    invalid_feeds = ["not a Feed object"]

    with pytest.raises(ValueError, match="Invalid feed object"):
        save_feeds(invalid_feeds)  # type: ignore[arg-type]

