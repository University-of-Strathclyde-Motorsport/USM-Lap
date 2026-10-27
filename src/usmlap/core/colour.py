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
        cls,
        source_type: Any,  # noqa:  S6542
        handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls, core_schema.str_schema()
        )


_N_COLOUR_LISTS: dict[int, list[str]] = {
    1: ["#003366"],
    2: ["#003366", "#FF6454"],
    3: ["#003366", "#F5E075", "#FF6454"],
    4: ["#003366", "#69C2CD", "#F5E075", "#FF6454"],
    5: ["#003366", "#69C2CD", "#F5E075", "#FD9055", "#FF6454"],
}

N_COLOUR_MAX = max(_N_COLOUR_LISTS.keys())


def get_n_colours(n: int) -> list[HexColour]:
    """Get a list of `n` colours.

    The maximum value of `n` is given by `N_COLOUR_MAX`.
    """
    if n not in _N_COLOUR_LISTS:
        raise ValueError(f"No colour list defined for {n} colours")
    return [HexColour(colour) for colour in _N_COLOUR_LISTS[n]]
