"""
This module contains code shared by all vehicle components.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar, Optional, Self

from pydantic import BaseModel

type JSONDict = dict[str, Any]


class Subsystem(BaseModel):
    """
    Abstract base class for vehicle subsystems.

    Provides functionality for loading from, and saving to, JSON.
    """

    @classmethod
    def from_json(cls, filepath: Path) -> Self:
        """
        Load a subsystem from a JSON file.

        Args:
            filepath (str): The path to the JSON file.

        Returns:
            subsystem (Self): The loaded subsystem.
        """
        with open(filepath, "r") as file:
            data = file.read()
            return cls.model_validate_json(data)

    def to_json(self) -> str:
        """
        Converts a subsystem to a JSON string.

        Args:
            self (Subsystem): The subsystem to convert.

        Returns:
            json_string (str): The JSON string representation of the subsystem.
        """
        return self.model_dump_json(indent=2)


class AbstractSubsystem(Subsystem):
    """
    Abstract base class for subsystems with different implementations.

    https://typethepipe.com/post/pydantic-discriminated-union/
    """

    _subtypes: ClassVar[dict[str, type]] = {}

    def __init_subclass__(
        cls: type[AbstractSubsystem], type: Optional[str] = None
    ) -> None:
        super().__init_subclass__()
        if type:
            cls.type = type
            if type in cls._subtypes:
                error_message = (
                    f"Class {cls.__name__} cannot be registered "
                    f"with polymorphic type '{type}' "
                    f"because it's already registered "
                    f"to {cls._subtypes[type].__name__}"
                )
                raise AttributeError(error_message)
            cls._subtypes[type] = cls

    @classmethod
    def get_subtype_dictionary(cls) -> dict[str, type]:
        return cls._subtypes
