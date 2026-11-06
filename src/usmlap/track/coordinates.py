"""Convert tracks into x and y coordinates."""

import numpy as np

from usmlap.core.datatypes import Array1D


def calculate_coordinates(
    length: Array1D,
    curvature: Array1D,
    initial_coordinates: tuple[float, float] = (0, 0),
    initial_heading: float = 0,
) -> tuple[Array1D, Array1D]:
    """Calculate the coordinates for each node of a track.

    Note that the lengths of the returned arrays are one greater than the length
    of the input arrays. The first to penultimate elements are the start
    coordinates of each node. The second to final elements are the end
    coordinates of each node.

    Args:
        length (Array1D): The length of each node.
        curvature (Array1D): The curvature of each node.
        initial_coordinates (tuple[float, float]): The x and y coordinates of
            the start of the track (default = ``(0, 0)``).
        initial_heading (float): The initial heading angle (default = ``0``).

    Returns:
        tuple[Array1D, Array1D]: The x and y coordinates of each node.

    """
    x_0, y_0 = initial_coordinates

    swept_angle = curvature * length
    heading_angle = initial_heading + np.cumsum(swept_angle) - swept_angle[0]

    chord_length = length.copy()
    idx = curvature != 0
    chord_length[idx] = (2 / curvature[idx]) * np.sin(swept_angle[idx] / 2)

    dx = np.cos(heading_angle) * chord_length
    dy = np.sin(heading_angle) * chord_length

    x = np.insert(np.cumsum(dx), 0, 0) + x_0
    y = np.insert(np.cumsum(dy), 0, 0) + y_0

    return x, y
