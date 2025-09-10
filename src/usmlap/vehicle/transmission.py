"""
This module models the transmission of a vehicle.
"""

from .common import Subsystem
from typing import Annotated
from annotated_types import MinLen
from pydantic import PositiveFloat


class Transmission(Subsystem):
    """
    The transmission of the vehicle.

    Transmits power from the motor to the wheels.

    Attributes:
        primary_gear_reduction (float): The reduction of the primary gear.
        final_gear_reduction (float): The reduction of the final gear.
        gear_ratio (list[float]): The ratios of the gears.
    """

    primary_gear_reduction: PositiveFloat
    final_gear_reduction: PositiveFloat
    gear_ratio: Annotated[list[PositiveFloat], MinLen(1)]

    @property
    def overall_gear_ratio(self) -> list[float]:
        gear_reduction = self.primary_gear_reduction * self.final_gear_reduction
        return [gear_reduction * ratio for ratio in self.gear_ratio]
