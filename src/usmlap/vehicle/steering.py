"""
This module models the steering system of a vehicle.
"""

from typing import Annotated

from annotated_types import Unit
from pydantic import PositiveFloat

from .common import Subsystem


class Steering(Subsystem):
    """
    The steering system of the vehicle.

    Attributes:
        steering_ratio (float):
            The ratio of steering angle to wheel angle.
            A steering ratio of 5 means that
            for every 5 degrees the steering wheel is rotated,
            the wheels rotate 1 degree.
        steering_wheel_radius (float):
            The radius of the steering wheel.
            Used for calculating steering torque.
    """

    steering_ratio: PositiveFloat
    steering_wheel_radius: Annotated[PositiveFloat, Unit("m")]

    def get_steering_wheel_angle(self, wheel_angle: float) -> float:
        """
        Calculate the steering wheel angle required for a given wheel angle.

        Args:
            wheel_angle (float):
                Angular displacement of the wheel from static
                (clockwise positive).

        Returns:
            steering_wheel_angle (float):
                Angular displacement of the steering wheel from neutral
                (clockwise positive).
        """
        return wheel_angle * self.steering_ratio

    def get_wheel_angle(self, steering_wheel_angle: float) -> float:
        """
        Calculate the wheel angle for a given steering angle.

        Args:
            steering_wheel_angle (float):
                Angular displacement of the steering wheel from neutral
                (clockwise positive).

        Returns:
            wheel_angle (float):
                Angular displacement of the wheels from static
                (clockwise positive).
        """
        return steering_wheel_angle / self.steering_ratio
