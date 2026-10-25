"""This module defines hex colours."""

import re
from typing import Any, Self

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

REGEXP = "^#[0-9A-Fa-f]{6}$"


class HexColour(str):
    """A hex colour string."""

    def __new__(cls, value: Any) -> Self:
        value = str(value)
        if not re.fullmatch(REGEXP, value):
            raise ValueError(
                f"Hex colour must match the regular expression '{REGEXP}'"
            )
        return super().__new__(cls, value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls, core_schema.str_schema()
        )
