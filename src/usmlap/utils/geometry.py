"""
This module contains utility functions for working with geometry,
such as calculating areas and volumes.
"""

from math import pi


def area_of_circle(diameter: float) -> float:
    """
    Calculate the area of a circle from its diameter.

    Args:
        diameter (float): Diameter of the circle.

    Returns:
        area (float): Area of the circle.
    """
    return pow(diameter, 2) * (pi / 4)
