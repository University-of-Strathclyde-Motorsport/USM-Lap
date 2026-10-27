"""This module provides a framework for loading and writing objects to files."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from io import TextIOWrapper
from pathlib import Path
from typing import Any, ClassVar, Self

import yamlrocks
from pydantic import BaseModel, ConfigDict

from usmlap.core.filepath import PROJECT_ROOT
from usmlap.core.registry import Registry

logger = logging.getLogger(__name__)


def load_yaml_dict(yaml: TextIOWrapper) -> dict[str, Any]:
    """Load a dictionary from a .yaml file."""
    data = yamlrocks.load(
        yaml, include_dir=PROJECT_ROOT, option=yamlrocks.OPT_INCLUDES
    )
    if isinstance(data, dict):
        return data
    raise ValueError("Yaml must be a dictionary, not an array")


@dataclass
class FileFormat:
    """Functions for reading and writing to a file format."""

    read_fcn: Callable[[TextIOWrapper], dict[str, Any]]
    write_fcn: Callable[[dict[str, Any], TextIOWrapper], None]


FileFormatRegistry = Registry[str, FileFormat]()
FileFormatRegistry.register(
    ".json", FileFormat(read_fcn=json.load, write_fcn=json.dump)
)
FileFormatRegistry.register(
    ".yaml", FileFormat(read_fcn=load_yaml_dict, write_fcn=yamlrocks.dump)
)


@dataclass
class LibraryLoadError(Exception):
    """Raised if an error occurs while loading a library object."""

    object_type: str
    filepath: Path

    def __str__(self) -> str:
        return f"Unable to load {self.object_type} from '{self.filepath}'"


@dataclass
class LibraryWriteError(Exception):
    """Raised if an error occurs while writing a library object."""

    object_type: str
    filepath: Path

    def __str__(self) -> str:
        return f"Unable to write {self.object_type} to '{self.filepath}'"


class Serialisable(BaseModel):
    """Base for classes which can be loaded and written to file."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

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
            return cls.from_file(Path(input))
        elif isinstance(input, Path):
            return cls.from_file(input)
        return input

    @classmethod
    def from_file(cls, filepath: Path) -> Self:
        try:
            logger.debug("Loading %s from '%s'", cls.__name__, filepath)
            file_format = FileFormatRegistry.get(filepath.suffix)
            with open(filepath, "r", encoding="utf-8") as file:
                data = file_format.read_fcn(file)
            return cls.model_validate(data)
        except Exception as e:
            raise LibraryLoadError(cls.__name__, filepath) from e

    def write_file(self, filepath: Path, *, overwrite: bool = False) -> None:
        if filepath.exists() and not overwrite:
            logger.warning(
                "Unable to save %s to '%s'; file already exists",
                self.__class__.__name__,
                filepath,
            )
            return

        try:
            file_format = FileFormatRegistry.get(filepath.suffix)
            filepath.parent.mkdir(exist_ok=True, parents=True)
            with open(filepath, "w", encoding="utf-8") as file:
                data = self.model_dump(mode="json")
                file_format.write_fcn(data, file)
            logger.info("%s written to '%s'", self.__class__.__name__, filepath)
        except Exception as e:
            raise LibraryWriteError(self.__class__.__name__, filepath) from e

    def as_dict(self) -> dict[str, Any]:
        """Convert the object to a dictionary."""
        return self.model_dump()
