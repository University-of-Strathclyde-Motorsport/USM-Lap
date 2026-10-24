"""This module defines hex colours."""

import re
from typing import Any, Self

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
