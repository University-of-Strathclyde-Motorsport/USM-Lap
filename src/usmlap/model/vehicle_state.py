"""
This module defines the variables associated with a vehicle's state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple

from usmlap.model.environment import AMBIENT_TEMPERATURE
from usmlap.utils.datatypes import FourCorner
from usmlap.vehicle.powertrain import CellState, StateOfCharge


class VehicleMotion(NamedTuple):
    """
    Variables describing the motion of the vehicle.

    Attributes:
        velocity (float): Velocity in the x direction.
        ax (float): Longitudinal acceleration (forwards +ve).
        ay (float): Lateral acceleration (left +ve).
    """

    velocity: float = 0
    ax: float = 0
    ay: float = 0


@dataclass
class TransientVariables(object):
    """
    Transient variables of the vehicle at a single instant.

    Attributes:
        soc (StateOfCharge): The state of charge of the accumulator.
            1 = fully charged, 0 = fully discharged (default = 1).
    """

    soc: StateOfCharge = StateOfCharge(1)
    cell_temperature: float = AMBIENT_TEMPERATURE

    @property
    def cell_state(self) -> CellState:
        return CellState(soc=self.soc, temperature=self.cell_temperature)

    @staticmethod
    def get_default() -> TransientVariables:
        """
        Get a state variable object with default values.
        """
        return TransientVariables()


@dataclass
class CalculatedVehicleState(object):
    """
    The full state of the vehicle at a point.
    """

    velocity: float
    ax: float
    ay: float
    weight: float
    centripetal_force: float
    downforce: float
    drag: float
    resistive_fx: float
    required_fy: float
    normal_force: float
    normal_loads: FourCorner[float]
    motor_speed: float
    motor_torque: float
    motor_power: float
    accumulator_current: float
    heating_power: float
    cooling_power: float

    @property
    def net_heating_power(self) -> float:
        return self.heating_power - self.cooling_power

    @property
    def long_lt(self) -> float:
        """Longitudinal load transfer."""
        return sum(self.normal_loads.front) - sum(self.normal_loads.rear)

    @property
    def lat_lt(self) -> float:
        """Lateral load transfer."""
        return sum(self.normal_loads.left) - sum(self.normal_loads.right)


@dataclass
class VehicleState(object):
    """
    Container for variables describing a vehicle's state.

    Attributes:
        motion (VehicleMotion): Variables describing the vehicle's motion.
        transient (TransientVariables): The vehicle's transient variables.
        calculated (CalculatedVehicleState): Full state of the vehicle.
    """

    motion: VehicleMotion
    transient: TransientVariables
    calculated: CalculatedVehicleState
