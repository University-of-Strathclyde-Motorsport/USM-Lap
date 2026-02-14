"""
This module models the driver of the vehicle.
"""

from .common import Component


class Driver(Component, library="drivers.json"):
    """
    The driver of the vehicle.

    Attributes:
        mass (float): Mass of the driver.
        height (float): Height of the driver.
    """

    mass: float
    height: float