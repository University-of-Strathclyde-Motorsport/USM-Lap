"""
This module models the transmission of a vehicle.
"""

from pydantic import PositiveFloat

from .common import Subsystem


class Transmission(Subsystem):
    """
    The transmission of the vehicle.

    Transmits power from the motor to the wheels.

    Attributes:
        final_drive_ratio (float):
            The overall gear reduction of the transmission.
            A final drive ratio of 3
            means that the drive axle rotates once
            for every 3 revolutions of the motor.
    """

    final_drive_ratio: PositiveFloat
