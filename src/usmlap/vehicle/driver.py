"""
This module models the driver of the vehicle."""

from usmlap.core.filepath import LIBRARY_ROOT
from usmlap.utils.library import HasLibrary


class Driver(HasLibrary, path=LIBRARY_ROOT / "drivers"):
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
