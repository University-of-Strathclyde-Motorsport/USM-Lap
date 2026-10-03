"""
This modules models the motor controller of a vehicle."""

from usmlap.core.filepath import LIBRARY_ROOT
from usmlap.utils.library import HasLibrary


class MotorController(
    HasLibrary,
    path=LIBRARY_ROOT / "components" / "motor_controllers",
):
    """
    A motor controller.

    Attributes:
        print_name (str): The printable name of the motor controller.
        resistance (float): The resistance of the motor controller.
        efficiency (float): The approximate efficiency of the motor controller.

    """

    print_name: str
    resistance: float
    efficiency: float
