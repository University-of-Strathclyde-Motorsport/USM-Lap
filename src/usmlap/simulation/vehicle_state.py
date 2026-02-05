"""
This module defines the variables associated with a vehicle's state.
"""

from dataclasses import dataclass

from utils.datatypes import FourCorner
from vehicle.aero import AeroAttitude
from vehicle.tyre.tyre_model import TyreAttitude


@dataclass
class StateVariables(object):
    """
    The state of the vehicle at a point.
    """

    velocity: float
    ax: float = 0


@dataclass
class FullVehicleState(object):
    """
    The full state of the vehicle at a point.
    """

    weight: float
    centripetal_force: float
    aero_attitude: AeroAttitude
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
    motor_force: float

    @property
    def total_lateral_traction(self) -> float:
        return sum(self.lateral_traction)
