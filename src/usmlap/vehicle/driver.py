"""
This module models the driver of the vehicle.
"""

from .common import Component


class Driver(Component):
    """
    The driver of the vehicle.

    Attributes:
        mass (float): Mass of the driver.
        height (float): Height of the driver.
    """

    mass: float
    height: float

    @classmethod
    def library_name(cls) -> str:
        return "drivers.json"
