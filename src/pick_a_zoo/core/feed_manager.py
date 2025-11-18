"""Feed manager library for loading and saving camera feed configurations.

This module follows the library-first architecture principle and is independently testable.
"""

import shutil
import tempfile
from pathlib import Path

import yaml
from loguru import logger
from platformdirs import user_data_dir

from pick_a_zoo.core.models import Feed


def get_config_path() -> Path:
    """Get the path to the feeds configuration file.

    Returns:
        Path: Path to feeds.yaml in platform-appropriate user data directory.
    """
    app_name = "pick-a-zoo"
    app_author = "pick-a-zoo"
    data_dir = Path(user_data_dir(app_name, app_author))
    config_path = data_dir / "feeds.yaml"
    return config_path


def load_feeds() -> list[Feed]:
    """Load camera feeds from the configuration file.

    Behavior:
        - If config file exists and is valid: parse YAML and return list of Feed objects
        - If config file is missing: create empty file with default structure, return []
        - If config file is corrupted: rebuild empty file, log warning, return []
        - If file is read-only: log error, return [] (do not crash)

    Returns:
        list[Feed]: List of Feed objects. Returns empty list if file is missing or corrupted.

    Raises:
        PermissionError: If file cannot be created due to permissions (propagated, not caught)
        OSError: If file system error occurs (propagated, not caught)
    """
    config_path = get_config_path()

    # Create parent directory if it doesn't exist
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as e:
        logger.error(f"Failed to create config directory: {e}")
        raise

    # Check if file exists
    if not config_path.exists():
        logger.info("Config file missing, creating empty file")
        _create_empty_config_file(config_path)
        return []

    # Try to load and parse the file
    try:
        with config_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Validate structure
        if data is None:
            logger.warning("Config file is empty, returning empty list")
            return []

        if not isinstance(data, dict):
            raise ValueError("Config file must contain a dictionary")

        feeds_data = data.get("feeds", [])
        if not isinstance(feeds_data, list):
            raise ValueError("'feeds' must be a list")

        # Parse feeds into Feed objects
        feeds = []
        for feed_data in feeds_data:
            try:
                feed = Feed(**feed_data)
                feeds.append(feed)
            except Exception as e:
                logger.warning(f"Invalid feed entry skipped: {e}")
                continue

        logger.info(f"Loaded {len(feeds)} feeds from config")
        return feeds

    except yaml.YAMLError as e:
        logger.warning(f"Config file corrupted (YAML parse error): {e}. Rebuilding empty file.")
        _create_empty_config_file(config_path)
        return []
    except (ValueError, KeyError) as e:
        logger.warning(f"Config file has invalid structure: {e}. Rebuilding empty file.")
        _create_empty_config_file(config_path)
        return []
    except (PermissionError, OSError) as e:
        logger.error(f"Failed to read config file: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading feeds: {e}", exc_info=True)
        _create_empty_config_file(config_path)
        return []


def save_feeds(feeds: list[Feed]) -> None:
    """Save camera feeds to the configuration file atomically.

    Args:
        feeds: List of Feed objects to save.

    Raises:
        ValueError: If any Feed object is invalid.
        PermissionError: If file cannot be written due to permissions.
        OSError: If file system error occurs.
    """
    # Validate all feeds before saving
    for feed in feeds:
        if not isinstance(feed, Feed):
            raise ValueError(f"Invalid feed object: {feed}")
        # Pydantic validation happens automatically when creating Feed objects

    config_path = get_config_path()

    # Create parent directory if it doesn't exist
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as e:
        logger.error(f"Failed to create config directory: {e}")
        raise

    # Prepare data for YAML serialization
    feeds_data = []
    for feed in feeds:
        feed_dict = feed.model_dump(mode="json")
        # Convert HttpUrl to string for YAML serialization
        feed_dict["url"] = str(feed_dict["url"])
        feeds_data.append(feed_dict)

    data = {"feeds": feeds_data}

    # Atomic write: write to temp file first, then rename
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False, dir=config_path.parent
        ) as tmp_file:
            tmp_path = Path(tmp_file.name)
            yaml.safe_dump(data, tmp_file, default_flow_style=False, sort_keys=False)

        # Atomic rename
        shutil.move(str(tmp_path), str(config_path))
        logger.info(f"Saved {len(feeds)} feeds to config")
    except (PermissionError, OSError) as e:
        logger.error(f"Failed to save feeds: {e}")
        # Clean up temp file if it exists
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass
        raise
    except Exception as e:
        logger.error(f"Unexpected error saving feeds: {e}", exc_info=True)
        # Clean up temp file if it exists
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass
        raise


def _create_empty_config_file(config_path: Path) -> None:
    """Create an empty configuration file with default structure.

    Args:
        config_path: Path to the configuration file.

    Raises:
        PermissionError: If file cannot be created due to permissions.
        OSError: If file system error occurs.
    """
    try:
        empty_data: dict[str, list] = {"feeds": []}
        with config_path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(empty_data, f, default_flow_style=False, sort_keys=False)
        logger.info("Created empty config file")
    except (PermissionError, OSError) as e:
        logger.error(f"Failed to create empty config file: {e}")
        raise

