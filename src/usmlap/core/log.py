"""
This module configures logging for the project.
"""

from logging.config import dictConfig
from pathlib import Path

import yaml

from usmlap.core.filepath import CONFIG_ROOT


def get_logging_config_file() -> Path:
    """Get the path to the logging configuration file."""
    return CONFIG_ROOT / "logging.yaml"


def configure_logging() -> None:
    """Configure logging for the project."""
    config_file = get_logging_config_file()
    if not config_file.exists():
        raise FileNotFoundError(
            f"Logging config file not found at {config_file}"
        )
    with open(config_file, "r") as f:
        config = yaml.safe_load(f.read())
        dictConfig(config)
