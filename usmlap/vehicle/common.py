from abc import ABC, abstractmethod
import json
from typing import Self, Any


class Subsystem:
    @classmethod
    def from_json(cls, filepath: str) -> Self:
        with open(filepath, "r") as file:
            return cls(**json.load(file))

    def to_json(self) -> str:
        return json.dumps(
            self,
            default=lambda object: object.__dict__,
            sort_keys=True,
            indent=4,
        )

    def __str__(self) -> str:
        return self.to_json()


class Component(ABC, Subsystem):
    @classmethod
    @abstractmethod
    def library_name(cls) -> str:
        pass

    @classmethod
    def _get_library_path(cls) -> str:
        return "library/components/" + cls.library_name()

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
