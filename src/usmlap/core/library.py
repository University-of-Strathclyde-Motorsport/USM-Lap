"""
This module provides a superclass which can be loaded from a .yaml file.
"""

import logging
from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SupportsLoading(BaseModel):
    """Base class for classes which can be loaded from files."""

    @classmethod
    def from_yaml(cls, filepath: Path) -> Self:
        """Load an object of the class from a .yaml file."""
        with open(filepath, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
        return cls.model_validate(data)

    def write_yaml(self, filepath: Path) -> None:
        """Write an object to a .yaml file."""
        with open(filepath, "w", encoding="utf-8") as file:
            data = self.model_dump(mode="json")
            yaml.dump(data, file)
        logger.info("%s written to '%s'", self.__class__.__name__, filepath)
