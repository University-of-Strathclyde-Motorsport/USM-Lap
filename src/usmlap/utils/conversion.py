"""
This module contains utility functions for converting between units.
"""

from math import pi


def degrees_to_radians(angle_degrees: float) -> float:
    """
    Convert an angle from degrees to radians.

    Args:
        angle_degrees (float): Angle in degrees.

    Returns:
        angle_radians (float): Angle in radians.
    """
    return angle_degrees * (pi / 180)


def radians_to_degrees(angle_radians: float) -> float:
    """
    Convert an angle from radians to degrees.

    Args:
        angle_radians (float): Angle in radians.

    Returns:
        angle_degrees (float): Angle in degrees.
    """
    return angle_radians * (180 / pi)
