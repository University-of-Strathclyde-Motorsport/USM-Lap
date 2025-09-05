"""
This module models the suspension of a vehicle.
"""

from .common import Subsystem
from typing import Annotated
from annotated_types import Unit
from pydantic import PositiveFloat


class SuspensionAxle(Subsystem):
    pass


class Suspension(Subsystem):
    """
    The suspension system of a vehicle.

    Attributes:
        front (SuspensionAxle): Front axle suspension
        rear (SuspensionAxle): Rear axle suspension
        wheelbase (float): The distance between the front and rear wheels, measured between contact patches
        front_track_width (float): The width of the front track, measured between contact patches
        rear_track_width (float): The width of the rear track, measured between contact patches
        centre_of_gravity_height (float): The height of the centre of gravity above the ground plane
    """

    front: SuspensionAxle
    rear: SuspensionAxle
    wheelbase: Annotated[PositiveFloat, Unit("m")]
    front_track_width: Annotated[PositiveFloat, Unit("m")]
    rear_track_width: Annotated[PositiveFloat, Unit("m")]
    centre_of_gravity_height: Annotated[PositiveFloat, Unit("m")]
