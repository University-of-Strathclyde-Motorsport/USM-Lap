"""
This module contains functions for mathematical operations.
"""

from typing import Optional


def clamp(
    value: float,
    *,
    minimum: Optional[float] = None,
    maximum: Optional[float] = None,
) -> float:
    """
    Clamp a value to a range.
    If `value` is below `minimum`, it is set to `minimum`.
    If `value` is above `maximum`, it is set to `maximum`.
    Otherwise, `value` is returned unchanged.
    """
    if minimum is not None:
        value = max(value, minimum)
    if maximum is not None:
        value = min(value, maximum)
    return value
