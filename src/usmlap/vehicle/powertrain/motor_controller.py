"""
This modules models the motor controller of a vehicle.
"""

from ..common import Component


class MotorController(Component):
    """
    A motor controller.

    Attributes:
        resistance: The resistance of the motor controller.
    """

    resistance: float

    @classmethod
    def library_name(cls) -> str:
        return "motor_controllers.json"
