"""
This modules models the motor controller of a vehicle.
"""

from ..common import Component


class MotorController(Component, library="motor_controllers"):
    """
    A motor controller.

    Attributes:
        print_name (str): The printable name of the motor controller.
        resistance (float): The resistance of the motor controller.
        efficiency (float): The efficiency of the motor controller (approximate).
    """

    print_name: str
    resistance: float
    efficiency: float
