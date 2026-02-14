"""
This modules models the motor controller of a vehicle.
"""

from ..common import Component


class MotorController(Component, library="motor_controllers.json"):
    """
    A motor controller.

    Attributes:
        resistance: The resistance of the motor controller.
        efficiency: The efficiency of the motor controller (approximate).
    """

    resistance: float
    efficiency: float

