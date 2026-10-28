"""Functions for common mathematical operations."""

import math

import numpy as np
import numpy.typing as npt


def clamp(
    value: float,
    *,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float:
    """
    Clamp a value to a range.
    If `value` is below `minimum`, it is set to `minimum`.
    If `value` is above `maximum`, it is set to `maximum`.
    Otherwise, `value` is returned unchanged.
    """
    if maximum is not None and minimum is not None and maximum < minimum:
        raise ValueError("'maximum' must be greater than or equal to 'minimum'")
    if minimum is not None:
        value = max(value, minimum)
    if maximum is not None:
        value = min(value, maximum)
    return value


def area_of_circle(diameter: float) -> float:
    """
    Calculate the area of a circle from its diameter.

    Diameter must be non-negative.

    Args:
        diameter (`float`): Diameter of the circle.

    Returns:
        `float`: Area of the circle.

    Raises:
        `ValueError`: if diameter is negative

    """
    if diameter < 0:
        raise ValueError(f"Invalid diameter {diameter}; must be non-negative")
    return (diameter**2) * (math.pi / 4)


def interp_previous[T: np.generic](
    x: npt.NDArray[np.float64],
    xp: npt.NDArray[np.float64],
    yp: npt.NDArray[T],
) -> npt.NDArray[T]:
    """Interpolate a list by choosing the previous  value.

    Args:
        x (`NDArray[float64]`):
            The x-coordinates at which to evaluate the interpolated values.
        xp (`NDArray[float64]`):
            The x-coordinates of the data. Must be strictly increasing.
        yp (`list[T]`):
            The y-coordinates of the data. Must be the same length as `xp`.

     Returns:
        y (list[T]): The interpolated values. The same length as `x`.

    Raises:
        ValueError:
            - If `xp` and `yp` are not the same length
            - If `xp` (or  `yp`) is empty
            - If `xp` is not strictly increasing
    """
    if len(xp) != len(yp):
        raise ValueError("xp and yp must have the same length")

    if len(xp) == 0:
        raise ValueError("xp and yp must not be empty")

    if not np.all(np.diff(xp) > 0):
        raise ValueError("xp must be strictly increasing")

    indices = np.searchsorted(xp, x, side="right") - 1
    indices = np.clip(indices, 0, len(yp) - 1)
    return yp[indices]
