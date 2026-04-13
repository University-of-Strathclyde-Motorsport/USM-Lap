"""
This module contains code shared by all vehicle components.
"""

from __future__ import annotations

from typing import Any, ClassVar, Optional

from pydantic import BaseModel

type JSONDict = dict[str, Any]


class AbstractSubsystem(BaseModel):
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
