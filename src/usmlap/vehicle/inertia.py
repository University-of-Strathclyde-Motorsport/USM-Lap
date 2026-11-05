"""This module models the inertia of a vehicle."""

from dataclasses import dataclass
from typing import Annotated

from annotated_types import Unit
from pydantic import PositiveFloat

from usmlap.core.datatypes import Percentage


@dataclass
class UnsprungMass:
    """Unsprung mass properties for a vehicle.

    Attributes:
        mass (Annotated[PositiveFloat, Unit("kg")]): Mass of the unsprung mass.
        centre_of_gravity_height (Annotated[PositiveFloat, Unit("m")]):
            Height of the centre of gravity above the ground plane.

    """

    mass: Annotated[PositiveFloat, Unit("kg")]
    centre_of_gravity_height: Annotated[PositiveFloat, Unit("m")]


@dataclass
class Inertia:
    """Inertia properties for a vehicle.

    Attributes:
        curb_mass (Annotated[PositiveFloat, Unit("kg")]): Mass of the vehicle.
        front_mass_distribution (Percentage): mass balance
        yaw_inertia (Annotated[PositiveFloat, Unit("kg.m^2")]): Yaw inertia of
            the vehicle.
        front_unsprung_mass (UnsprungMass): Unsprung mass for the front axle.
        rear_unsprung_mass (UnsprungMass): Unsprung mass for the rear axle.

    """

    curb_mass: Annotated[PositiveFloat, Unit("kg")]
    front_mass_distribution: Percentage
    yaw_inertia: Annotated[PositiveFloat, Unit("kg.m^2")]
    front_unsprung_mass: UnsprungMass
    rear_unsprung_mass: UnsprungMass
    equivalent_drivetrain_inertia: Annotated[PositiveFloat, Unit("kg")]
