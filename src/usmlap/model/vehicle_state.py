"""
This module defines the variables associated with a vehicle's state.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from usmlap.model.environment import AMBIENT_TEMPERATURE
from usmlap.utils.datatypes import FourCorner
from usmlap.vehicle.powertrain import CellState, StateOfCharge


@dataclass(slots=True)
class Trajectory(object):
    """
    Variables describing the trajectory of the vehicle.

    Attributes:
        curvature (float): Curvature of the track (left +ve).
        velocity (float): Longitudinal velocity.
        ax (float): Longitudinal acceleration (forwards +ve).
        ay (float): Lateral acceleration (left +ve).
    """

    curvature: float = 0
    velocity: float = 0
    ax: float = 0

    @property
    def ay(self) -> float:
        return self.velocity**2 * self.curvature

    @ay.setter
    def ay(self, value: float) -> None:
        self.velocity = math.sqrt(value / self.curvature)


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
        trajectory (Trajectory): Variables describing the vehicle's trajectory.
        transient (TransientVariables): The vehicle's transient variables.
        calculated (CalculatedVehicleState): Full state of the vehicle.
    """

    trajectory: Trajectory
    transient: TransientVariables
    calculated: CalculatedVehicleState
