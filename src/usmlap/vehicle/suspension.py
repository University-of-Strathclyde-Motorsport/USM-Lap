"""
This module models the suspension of a vehicle.
"""

from .common import Subsystem
from typing import Literal, Annotated, Union
from annotated_types import Unit
from pydantic import Field, PositiveFloat
from abc import ABC


class SuspensionAxle(Subsystem, ABC):
    """
    Abstract base class for suspension on a single axle of a vehicle.

    Attributes:
        track_width (float):
            The width of the track, measured between contact patches.
    """

    track_width: Annotated[PositiveFloat, Unit("m")]


class DecoupledSuspension(SuspensionAxle):
    """
    Decoupled suspension system.
    """

    suspension_type: Literal["decoupled"]

    roll_centre_height: Annotated[PositiveFloat, Unit("m")]
    heave_motion_ratio: PositiveFloat
    heave_spring_rate: Annotated[PositiveFloat, Unit("N/m")]
    roll_motion_ratio: PositiveFloat
    roll_spring_rate: Annotated[PositiveFloat, Unit("N/m")]


class AlternativeSuspension(SuspensionAxle):
    """
    Alternative suspension system.
    """

    suspension_type: Literal["alternative"]


SuspensionImplementation = Annotated[
    Union[DecoupledSuspension, AlternativeSuspension],
    Field(discriminator="suspension_type"),
]


class Suspension(Subsystem):
    """
    The suspension system of a vehicle.

    Attributes:
        front (DecoupledSuspension):
            Front axle suspension.
        rear (DecoupledSuspension):
            Rear axle suspension.
        wheelbase (float):
            The distance between the front and rear wheels,
            measured between contact patches.
        front_track_width (float):
            The width of the front track,
            measured between contact patches.
        rear_track_width (float):
            The width of the rear track,
            measured between contact patches.
        centre_of_gravity_height (float):
            The height of the centre of gravity above the ground plane.
    """

    front: SuspensionImplementation
    rear: SuspensionImplementation
    wheelbase: Annotated[PositiveFloat, Unit("m")]
    centre_of_gravity_height: Annotated[PositiveFloat, Unit("m")]
