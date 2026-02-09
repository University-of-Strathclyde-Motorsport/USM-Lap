"""
This module defines the variables associated with a vehicle's state.
"""

from __future__ import annotations

from dataclasses import dataclass

from utils.datatypes import FourCorner
from vehicle.tyre.tyre_model import TyreAttitude


@dataclass
class StateVariables(object):
    """
    The state of the vehicle at a point.
    """

    velocity: float
    ax: float = 0
    state_of_charge: float = 1

    @staticmethod
    def get_empty() -> StateVariables:
        return StateVariables(velocity=0)


@dataclass
class FullVehicleState(object):
    """
    The full state of the vehicle at a point.
    """

    weight: float
    centripetal_force: float
    downforce: float
    drag: float
    resistive_fx: float
    required_fy: float
    normal_force: float
    normal_loads: FourCorner[float]
    tyre_attitudes: FourCorner[TyreAttitude]
    lateral_traction: FourCorner[float]
    longitudinal_traction: FourCorner[float]
    motor_speed: float
    motor_torque: float
    motor_power: float
    accumulator_power: float
    motor_force: float

    @property
    def total_lateral_traction(self) -> float:
        return sum(self.lateral_traction)

    @staticmethod
    def get_empty() -> FullVehicleState:
        return FullVehicleState(
            weight=0,
            centripetal_force=0,
            downforce=0,
            drag=0,
            resistive_fx=0,
            required_fy=0,
            normal_force=0,
            normal_loads=FourCorner([0, 0, 0, 0]),
            tyre_attitudes=FourCorner(
                [
                    TyreAttitude(normal_load=0),
                    TyreAttitude(normal_load=0),
                    TyreAttitude(normal_load=0),
                    TyreAttitude(normal_load=0),
                ]
            ),
            lateral_traction=FourCorner([0, 0, 0, 0]),
            longitudinal_traction=FourCorner([0, 0, 0, 0]),
            motor_speed=0,
            motor_torque=0,
            motor_power=0,
            accumulator_power=0,
            motor_force=0,
        )
