"""
This module contains functions for working with arrays.
"""

import math
from typing import TypeVar

T = TypeVar("T")


def interp_previous(x: list[float], xp: list[float], yp: list[T]) -> list[T]:
    """
    Interpolate a list of values by choosing the previous value.

    Args:
        x (list[float]):
            The x-coordinates at which to evaluate the interpolated values.
        xp (list[float]):
            The x-coordinates of the data points. Must be strictly increasing.
        yp (list[T]):
            The y-coordinates of the data points. Must be the same length as xp.

    Returns:
        y (list[T]): The interpolated values. The same length as x.
    """
    assert len(xp) == len(yp), "xp and yp must have the same length"
    xp.append(math.inf)
    yp.append(yp[-1])

    pos = 0
    y: list[T] = []

    for i in range(len(x)):
        while x[i] >= xp[pos + 1]:
            pos += 1
        y.append(yp[pos])

    return y


def diff(x: list[float]) -> list[float]:
    """
    Compute the difference between consecutive elements of a list.

    Args:
        x (list[float]): The input list.

    Returns:
        y (list[float]): The difference between consecutive elements of x.
            y has one fewer elements than x.
    """
    assert len(x) > 1, "x must have at least two elements"
    return [x[i + 1] - x[i] for i in range(len(x) - 1)]
