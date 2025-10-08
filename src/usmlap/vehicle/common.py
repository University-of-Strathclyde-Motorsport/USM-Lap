"""
This module contains code shared by all vehicle components.
"""

from abc import ABC, abstractmethod
from pydantic import BaseModel, model_validator
import json
from typing import Self, Any


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
        return self.model_dump_json(indent=4)

    def __str__(self) -> str:
        return self.to_json()


class Component(ABC, Subsystem):
    """
    Abstract base class for vehicle components.

    Provides functionality for loading components from a library.
    """

    name: str

    @classmethod
    @abstractmethod
    def library_name(cls) -> str: ...

    @classmethod
    def _get_library_path(cls) -> str:
        """
        Get the path to the component library.

        Returns:
            library_path (str): Path to the component library.
        """
        return "appdata/library/components/" + cls.library_name()

    @classmethod
    def load_library(cls) -> dict[str, dict[str, Any]]:
        """
        Load the component library as a dictionary.

        The library is loaded from a JSON file,
        specified by the  `library_name` method.

        Returns:
            library (dict[str, dict[str, Any]]):
                A dictionary of components.
                The component names are used as keys.
                The values are dictionaries containing component data.
        """
        with open(cls._get_library_path(), "r") as library_file:
            return json.load(library_file)

    @classmethod
    def list_components(cls) -> list[str]:
        """
        Get a list

        Returns:
            list[str]: _description_
        """
        return list(cls.load_library().keys())

    @classmethod
    def check_component_exists(cls, name: str) -> None:
        """
        Check if a component exists in the library.

        Args:
            name (str): The name of the component.

        Raises:
            KeyError: If no component with the given name is found.
        """
        components = cls.list_components()
        if name not in components:
            error_message = (
                f"Component '{name}' not found "
                f"in library '{cls.library_name()}' "
                f"(available components: {components})"
            )
            raise KeyError(error_message)

    @classmethod
    def get_component(cls, name: str) -> dict[str, Any]:
        """
        Select a component from the library.

        The name of the component is added to the returned dictionary.

        Args:
            name (str): The name of the component.

        Raises:
            KeyError: If no component with the given name is found.

        Returns:
            component (dict[str, Any]):
                A dictionary containing the component data.
        """
        cls.check_component_exists(name)
        library = cls.load_library()
        component = library[name]
        component["name"] = name
        return component

    @classmethod
    def from_library(cls, name: str) -> Self:
        """
        Create a component object from the library.

        Args:
            name (str): The name of the component.

        Raises:
            KeyError: If no component with the given name is found.

        Returns:
            component (Component): A component object.
        """
        dictionary = cls.get_component(name)
        return cls.model_validate(dictionary)

    @model_validator(mode="before")
    @classmethod
    def expand_component(cls, data: Any) -> Any:
        """
        JSON deserialiser.

        If a component is specified by a string,
        this is looked up in the corresponding component library
        and expanded into a dictionary
        containing the component data.
        """
        if isinstance(data, str):
            data = cls.get_component(data)
        return data
