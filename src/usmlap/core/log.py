"""This module configures logging for the project."""

import logging
from collections.abc import Generator
from contextlib import contextmanager
from logging import FileHandler, Formatter
from logging.config import dictConfig
from pathlib import Path
from typing import Any

import yaml

from usmlap.core.filepath import CONFIG_ROOT


def get_logging_config_file() -> Path:
    """Get the path to the logging configuration file."""
    return CONFIG_ROOT / "logging.yaml"


def _load_logging_config() -> dict[str, Any]:
    """Load logging config from file."""
    config_file = get_logging_config_file()
    with open(config_file) as f:
        return yaml.safe_load(f.read())


def configure_logging() -> None:
    """Configure logging for the project."""
    dictConfig(_load_logging_config())


configure_logging()


def _make_file_handler(
    log_file: Path, level: int | str, formatter: Formatter
) -> FileHandler:
    """Make a file handler for logging to a custom file."""
    handler = FileHandler(log_file, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(formatter)
    return handler


@contextmanager
def log_to_file(log_file: Path) -> Generator[None]:
    """Context manager which logs to a custom file."""
    logger = logging.getLogger(__name__)
    logger.debug("Starting logging to '%s'", log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    config = _load_logging_config()
    handler_config = config["handlers"]["log_file"]
    log_level = handler_config.get("level", logging.INFO)
    formatter = Formatter(**config["formatters"][handler_config["formatter"]])
    file_handler = _make_file_handler(log_file, log_level, formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)

    try:
        yield
    finally:
        root_logger.removeHandler(file_handler)
        file_handler.close()
        logger.debug("Stopping logging to '%s'", log_file)
