"""
This module provides an interface for loading and saving objects from a library.
"""

from __future__ import annotations

from abc import ABC
from pathlib import Path
from typing import Any, ClassVar, Generator, Self

from pydantic import BaseModel, ValidationError, model_validator

from usmlap.filepath import LIBRARY_ROOT as LIBRARY_ROOT  # noqa: S1128

JSON_INDENT = 2  # Number of spaces to indent JSON files


class LibraryNotFoundError(KeyError):
    """
    Raised if a library cannot be found.

    Args:
        library (type[HasLibrary]): The type for which no library can be found.
        path (Path): The path to the library.
    """

    def __init__(self, library: type[HasLibrary], path: Path) -> None:
        super().__init__(f"'{library.__name__}' library not found at {path}.")
        self.library = library
        self.path = path


class ItemNotFoundError(KeyError):
    """
    Raised if an item cannot be found in the library.

    Args:
        item (str): The name of the item.
        library (str): The name of the library.
        available (list[str]): A list of available items.
    """

    def __init__(self, item: str, library: str, available: list[str]) -> None:
        super().__init__(
            f"Item '{item}' not found in {library} library. "
            f"Available items: {available}"
        )
        self.item = item
        self.library = library
        self.available = available


class FailedToValidateItem(Exception):
    """
    Raised if an item cannot be validated.

    Args:
        item (str): The name of the item.
        library (str): The name of the library.
        validation_error (ValidationError): The validation error.
    """

    def __init__(
        self, item: str, library: str, validation_error: ValidationError
    ) -> None:
        super().__init__(
            f"Failed to validate {item} in {library} library. "
            f"Error: {validation_error}"
        )
        self.item = item
        self.library = library
        self.validation_error = validation_error


class HasLibrary(ABC, BaseModel):
    """
    Base class for objects that have a library.
    """

    _library_path: ClassVar[Path]
    _files: ClassVar[dict[str, Path]]
    _library: dict[str, Self]

    def __init_subclass__(cls: type[HasLibrary], path: Path) -> None:
        super().__init_subclass__()
        cls._library_path = path
        cls.refresh_items()
        cls._library = {}

    @classmethod
    def refresh_items(cls) -> None:
        cls._files = {file.stem: file for file in cls._iter_filepaths()}

    @classmethod
    def from_json(cls, filepath: str | Path) -> Self:
        """
        Load and validate an object from a JSON file.

        Args:
            filepath (str | Path): The path to the JSON file.

        Returns:
            object (Self): The loaded, validated object.

        Raises:
            FileNotFoundError: If the file is not found.
            ValidationError: If the object cannot be validated.
        """
        if isinstance(filepath, str):
            return cls._load_item(filepath)

        with open(filepath, "r") as file:
            data = file.read()
            return cls.model_validate_json(data)

    def to_json(self) -> str:
        """
        Get a JSON representation of the object.

        Returns:
            str: JSON representation of the object.
        """
        return self.model_dump_json(indent=JSON_INDENT)

    def __str__(self) -> str:
        return self.to_json()

    @classmethod
    def _get_library_path(cls) -> Path:
        """
        Get the path to the library.

        Returns:
            path (Path): Path to the library.
        """
        path = cls._library_path
        if not path.is_dir():
            raise LibraryNotFoundError(library=cls, path=path)

        return path

    @classmethod
    def _iter_filepaths(cls) -> Generator[Path, None, None]:
        return cls._get_library_path().iterdir()

    @classmethod
    def list_items(cls) -> list[str]:
        """
        Get a list of available items in the library.

        Returns:
            items (list[str]): Available item names.
        """
        return list(cls._files.keys())

    @classmethod
    def item_exists(cls, item: str) -> bool:
        """
        Check if an item exists in the library.

        Args:
            item (str): The name of the file containing the item (no extension).
        """
        return item in cls._files

    @classmethod
    def _load_item(cls, name: str) -> Self:
        """
        Load an item from the library.

        Args:
            name (str): The name of the file containing the item (no extension).

        Returns:
            item (Self): The loaded item.
        """

        filepath = cls._files.get(name, None)
        if filepath is None:
            raise ItemNotFoundError(
                name, cls._library_path.name, cls.list_items()
            )
        return cls.from_json(filepath)

    @classmethod
    def library(cls) -> dict[str, Self]:
        cls._load_library()
        return cls._library

    @classmethod
    def _load_library(cls) -> None:
        """
        Loads the library into a dictionary.

        Any items that cannot be validated are skipped.

        Returns:
            library (dict[str, Self]): A dictionary of items.
        """
        print(f"Loading {cls.__name__} library...")
        for item in cls._files:
            try:
                cls.get_item(item)
            except ValidationError as error:
                raise FailedToValidateItem(item, cls.__name__, error)
                # TODO: Log a warning here
                continue

    @classmethod
    def get_item(cls, name: str) -> Self:
        """
        Select a component from the library.

        The name of the component is added to the returned dictionary.

        Args:
            name (str): The name of the component.

        Raises:
            KeyError: If no component with the given name is found.

        Returns:
            component (JSONDict):
                A dictionary containing the component data.
        """
        if name not in cls._library:
            cls._library[name] = cls._load_item(name)
        return cls._library[name]

    @model_validator(mode="before")
    @classmethod
    def expand_item(cls, data: Any) -> Any:
        """
        JSON deserialiser.

        If a component is specified by a string,
        this is looked up in the corresponding component library
        and expanded into a dictionary
        containing the component data.

        Args:
            data (Any): The data to expand.

        Returns:
            data (Any): The expanded data.

        Raises:
            ComponentNotFoundError:
                No suitable component cannot be found in the library.
        """
        if isinstance(data, str):
            data = cls.get_item(data).model_dump()
        return data
