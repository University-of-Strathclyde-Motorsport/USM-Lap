"""
This module models the inertia of a vehicle.
"""

from .common import Subsystem
from datatypes import Percentage
from typing import Annotated
from annotated_types import Unit
from pydantic import PositiveFloat


class UnsprungMass(Subsystem):
    """
    Unsprung mass properties for a vehicle.

    Attributes:
        mass (float): Mass of the unsprung mass.
        centre_of_gravity_height (float):
            Height of the centre of gravity above the ground plane.
    """

    mass: Annotated[PositiveFloat, Unit("kg")]
    centre_of_gravity_height: Annotated[PositiveFloat, Unit("m")]


class Inertia(Subsystem):
    """
    Inertia properties for a vehicle.

    Args:
        curb_mass (float): Mass of the vehicle.
        front_mass_distribution (float): mass balance
        yaw_inertia (float): Yaw inertia of the vehicle.
        centre_of_gravity_height (float):
            Height of the centre of gravity above the ground plane.
        front_unsprung_mass (UnsprungMass): Unsprung mass for the front axle.
        rear_unsprung_mass (UnsprungMass): Unsprung mass for the rear axle.
    """

    curb_mass: Annotated[PositiveFloat, Unit("kg")]
    front_mass_distribution: Percentage
    centre_of_gravity_height: Annotated[PositiveFloat, Unit("m")]
    yaw_inertia: Annotated[PositiveFloat, Unit("kg.m^2")]
    front_unsprung_mass: UnsprungMass
    rear_unsprung_mass: UnsprungMass
