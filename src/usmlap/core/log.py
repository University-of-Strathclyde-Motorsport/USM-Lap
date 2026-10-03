"""
This module configures logging for the project."""

import logging
from collections.abc import Generator
from contextlib import contextmanager
from logging import FileHandler
from logging.config import dictConfig
from pathlib import Path

import yaml

from usmlap.core.filepath import CONFIG_ROOT


def get_logging_config_file() -> Path:
    """
    Get the path to the logging configuration file."""
    return CONFIG_ROOT / "logging.yaml"


def configure_logging() -> None:
    """
    Configure logging for the project."""
    config_file = get_logging_config_file()
    if not config_file.exists():
        raise FileNotFoundError(
            f"Logging config file not found at {config_file}",
        )
    with open(config_file) as f:
        config = yaml.safe_load(f.read())
        dictConfig(config)


configure_logging()


@contextmanager
def log_to_file(log_file: Path) -> Generator[None]:
    """Context manager which logs to a custom file."""
    logger = logging.getLogger(__name__)
    logger.debug("Starting logging to '%s'", log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    try:
        yield
    finally:
        root_logger.handlers = [
            h for h in root_logger.handlers if h is not file_handler
        ]
        logger.debug("Stopping logging to '%s'", log_file)
