"""Unit tests for the `usmlap.core.log` module."""

import logging
from pathlib import Path

# import pytest
from usmlap.core.log import log_to_file

logger = logging.getLogger(__name__)


def test_log_to_file(tmp_path: Path):
    log_file = tmp_path / "test.log"
    logger.info("Log 1 (not logged to file)")
    with log_to_file(log_file):
        logger.info("Log 2 (logged to file)")
        logger.warning("Log 3 (logged to file)")
    logger.info("Log 4 (not logged to file)")

    with open(log_file, "r", encoding="utf-8") as f:
        log_contents = f.read()

    assert "Log 1" not in log_contents
    assert "Log 2" in log_contents
    assert "Log 3" in log_contents
    assert "Log 4" not in log_contents
