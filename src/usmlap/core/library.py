"""
This module provides a superclass which can be loaded from a .yaml file.
"""

from pathlib import Path
from typing import Self

import yaml
from pydantic import BaseModel


class SupportsLoading(BaseModel):
    """Base class for classes which can be loaded from files."""

    @classmethod
    def from_yaml(cls, filepath: Path) -> Self:
        """Load an object of the class from a .yaml file."""
        with open(filepath, "r") as file:
            data = yaml.safe_load(file)
        return cls.model_validate(data)
