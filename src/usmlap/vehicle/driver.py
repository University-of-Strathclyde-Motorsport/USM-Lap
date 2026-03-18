"""
This module models the driver of the vehicle.
"""

from .common import Component


class Driver(Component, library="components/drivers"):
    """
    The driver of the vehicle.

    Attributes:
        print_name (str): Printable name of the driver.
        mass (float): Mass of the driver.
        height (float): Height of the driver.
    """

    print_name: str
    mass: float
    height: float
