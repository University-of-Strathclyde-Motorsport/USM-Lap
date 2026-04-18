"""
This module defines the variables associated with a vehicle's state.
"""

from __future__ import annotations

from dataclasses import dataclass

from usmlap.model.environment import AMBIENT_TEMPERATURE
from usmlap.vehicle.powertrain import CellState, StateOfCharge


@dataclass
class StateVariables(object):
    """
    The state of the vehicle at a point.

    Attributes:
        state_of_charge (float): The state of charge of the accumulator.
            1 = fully charged, 0 = fully discharged
            (default = 1).
    """

    state_of_charge: StateOfCharge = StateOfCharge(1)
    cell_temperature: float = AMBIENT_TEMPERATURE

    @property
    def cell_state(self) -> CellState:
        return CellState(
            soc=self.state_of_charge, temperature=self.cell_temperature
        )

    @staticmethod
    def get_default() -> StateVariables:
        """
        Get a state variable object with default values.
        """
        return StateVariables()


@dataclass
class FullVehicleState(object):
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
    motor_speed: float
    motor_torque: float
    motor_power: float
    accumulator_current: float
    heating_power: float
    cooling_power: float

    @property
    def net_heating_power(self) -> float:
        return self.heating_power - self.cooling_power
