"""
This module contains code shared by all vehicle components.
"""

from abc import ABC, abstractmethod
from pydantic import BaseModel
import json
from typing import Self


class Subsystem(BaseModel):
    """
    Abstract base class for vehicle subsystems.

    Provides functionality for loading from, and saving to, JSON.
    """

    @classmethod
    def from_json(cls, filepath: str) -> Self:
        """
        Load a subsystem from a JSON file.

        Args:
            filepath (str): The path to the JSON file.

        Returns:
            subsystem (Self): The loaded subsystem.
        """
        with open(filepath, "r") as file:
            return cls.model_validate_json(file.read())

    def to_json(self) -> str:
        """
        Converts a subsystem to a JSON string.

        Args:
            self (Subsystem): The subsystem to convert.

        Returns:
            json_string (str): The JSON string representation of the subsystem.
        """
        return self.model_dump_json(indent=4)

    def __str__(self) -> str:
        return self.to_json()


class Component(ABC, Subsystem):
    """
    Abstract base class for vehicle components.

    Provides functionality for loading components from a library.
    """

    @classmethod
    @abstractmethod
    def library_name(cls) -> str:
        pass

    @classmethod
    def _get_library_path(cls) -> str:
        return "appdata/library/components/" + cls.library_name()

    @classmethod
    def load_library(cls) -> dict[str, Self]:
        with open(cls._get_library_path(), "r") as library_file:
            library = json.load(library_file)
            return {
                name: cls(**dictionary) for name, dictionary in library.items()
            }

    @classmethod
    def from_library(cls, name: str) -> Self:
        library = cls.load_library()
        library_name = cls.library_name()
        if name not in library:
            raise KeyError(
                f"Component '{name}' not found in library '{library_name}'"
                f" (available components: {list(library.keys())})"
            )
        return library[name]
