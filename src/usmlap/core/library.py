"""
This module provides a superclass which can be loaded from a .yaml file.
"""

import json
import logging
from collections.abc import Iterator
from pathlib import Path
from typing import ClassVar, Self

import yaml
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SupportsLoading(BaseModel):
    """Base class for classes which can be loaded from files."""

    _library: ClassVar[Path | None]

    @classmethod
    def __init_subclass__(cls, library: Path | None = None) -> None:
        super(cls).__init_subclass__()
        cls._library = library

    @classmethod
    def has_library(cls) -> bool:
        return cls._library is not None

    @classmethod
    def iter_library(cls) -> Iterator[Path]:
        if cls._library is None:
            raise ValueError(f"{cls.__name__} does not have a library")
        return cls._library.iterdir()

    @classmethod
    def initialise(cls, input: str | Path | Self) -> Self:
        """
        Method designed for use as a BeforeValidator.
        If input is a filepath, an object will be loaded from file.
        Otherwise, the input will be returned.
        """
        if isinstance(input, str):
            return cls.from_json(Path(input))
        elif isinstance(input, Path):
            return cls.from_json(input)
        return input

    @classmethod
    def from_yaml(cls, filepath: Path) -> Self:
        """Load an object of the class from a .yaml file."""
        logger.debug("Loading %s from '%s'", cls.__name__, filepath)
        with open(filepath, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
        return cls.model_validate(data)

    def write_yaml(self, filepath: Path) -> None:
        """Write an object to a .yaml file."""
        with open(filepath, "w", encoding="utf-8") as file:
            data = self.model_dump(mode="json")
            yaml.dump(data, file)
        self._log_write_to_file(filepath)

    @classmethod
    def from_json(cls, filepath: Path) -> Self:
        """Load an object of the class from a .json file."""
        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)
        return cls.model_validate(data)

    def write_json(self, filepath: Path) -> None:
        """Write an object to a .json file."""
        with open(filepath, "w", encoding="utf-8") as file:
            data = self.model_dump(mode="json")
            json.dump(data, file)
        self._log_write_to_file(filepath)

    def _log_write_to_file(self, filepath: Path) -> None:
        """Log a message when an object is written to file."""
        logger.info("%s written to '%s'", self.__class__.__name__, filepath)
