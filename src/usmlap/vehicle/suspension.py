"""
This module models the suspension of a vehicle."""

from abc import ABC
from dataclasses import dataclass
from typing import Annotated

from annotated_types import Unit
from pydantic import BaseModel, BeforeValidator, PlainSerializer, PositiveFloat

from usmlap.core.registry import Registry


class SuspensionModel(ABC):  # noqa: B024
    """
    Abstract base class for suspension on a single axle of a vehicle.

    Currently does nothing! (sorry Chris)
    """


class DecoupledSuspension(SuspensionModel):
    """
    Decoupled suspension, with separate heave and roll springs.
    """


SuspensionModelRegistry = Registry[str, type[SuspensionModel]](
    "suspension model"
)
SuspensionModelRegistry.register("decoupled", DecoupledSuspension)


class SuspensionAxle(BaseModel):
    """The suspension system on one axle of a vehicle."""

    suspension_model: Annotated[
        type[SuspensionModel],
        BeforeValidator(SuspensionModelRegistry.get_or_raise),
        PlainSerializer(SuspensionModelRegistry.get_key),
    ]
    roll_centre_height: Annotated[PositiveFloat, Unit("m")]
    heave_motion_ratio: PositiveFloat
    heave_spring_rate: Annotated[PositiveFloat, Unit("N/m")]
    roll_motion_ratio: PositiveFloat
    roll_spring_rate: Annotated[PositiveFloat, Unit("N/m")]
    track_width: Annotated[PositiveFloat, Unit("m")]


@dataclass
class Suspension:
    """
    The suspension system of a vehicle.

    Attributes:
        front (SuspensionModel):
            Front axle suspension.
        rear (SuspensionModel):
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

    front: SuspensionAxle
    rear: SuspensionAxle
    wheelbase: Annotated[PositiveFloat, Unit("m")]
    centre_of_gravity_height: Annotated[PositiveFloat, Unit("m")]
