"""
This module defines the interface for vehicle models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

# from math import cos, sin
from pydantic import BaseModel

from simulation.environment import Environment
from track.mesh import TrackNode
from utils.datatypes import FourCorner
from vehicle.aero import AeroAttitude
from vehicle.tyre.tyre_model import TyreAttitude
from vehicle.vehicle import Vehicle


class StateVariables(BaseModel):
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


class VehicleModelInterface(ABC):
    """
    Abstract base class for vehicle models.
    """

    vehicle: Vehicle
    environment: Environment

    def __init__(self, vehicle: Vehicle, environment: Environment) -> None:
        self.vehicle = vehicle
        self.environment = environment

    def resolve_vehicle_state(
        self, vehicle: Vehicle, state_variables: StateVariables, node: TrackNode
    ) -> FullVehicleState:
        """
        Calculate the full state of the vehicle at a node.

        Args:
            state_variables (StateVariables): The vehicle's state variables.
            node (TrackNode): The track node to evaluate.

        Returns:
            vehicle_state (FullVehicleState): The full state of the vehicle,
                including forces, torques, and energy.
        """
        weight = vehicle.total_mass * self.environment.gravity
        centripetal_force = (
            vehicle.total_mass * state_variables.velocity**2 * node.curvature
        )

        aero_attitude = AeroAttitude(
            velocity=state_variables.velocity,
            air_density=self.environment.air_density,
        )
        downforce = self.vehicle.aero.get_downforce(aero_attitude)
        drag = self.vehicle.aero.get_drag(aero_attitude)

        resistive_fx = drag + node.z_to_x(weight)
        required_fy = node.y_to_y(centripetal_force) + node.z_to_y(weight)
        normal_force = (
            node.z_to_z(weight) + node.y_to_z(centripetal_force) + downforce
        )

        normal_loads = self.get_normal_loads(normal_force)
        tyre_attitudes = self.get_tyre_attitudes(normal_loads)
        lateral_traction = self.get_lateral_traction(
            tyre_attitudes, resistive_fx
        )
        longitudinal_traction = self.get_longitudinal_traction(
            tyre_attitudes, required_fy
        )

        motor_speed = vehicle.velocity_to_motor_speed(state_variables.velocity)
        motor_torque = vehicle.powertrain.get_motor_torque(
            state_of_charge=1,  # TODO
            current=vehicle.powertrain.accumulator.maximum_discharge_current,
            motor_speed=motor_speed,
        )
        motor_force = vehicle.motor_torque_to_drive_force(motor_torque)

        return FullVehicleState(
            weight=weight,
            centripetal_force=centripetal_force,
            aero_attitude=aero_attitude,
            downforce=downforce,
            drag=drag,
            resistive_fx=resistive_fx,
            required_fy=required_fy,
            normal_force=normal_force,
            normal_loads=normal_loads,
            tyre_attitudes=tyre_attitudes,
            lateral_traction=lateral_traction,
            longitudinal_traction=longitudinal_traction,
            motor_speed=motor_speed,
            motor_torque=motor_torque,
            motor_force=motor_force,
        )

    @abstractmethod
    def lateral_vehicle_model(self, node: TrackNode) -> StateVariables:
        pass

    @abstractmethod
    def calculate_acceleration(
        self, state_variables: StateVariables, node: TrackNode
    ) -> float:
        pass

    @abstractmethod
    def calculate_decceleration(
        self, state_variables: StateVariables, node: TrackNode
    ) -> float:
        pass

    @abstractmethod
    def get_normal_loads(self, normal_force: float) -> FourCorner[float]:
        pass

    @abstractmethod
    def get_tyre_attitudes(
        self, normal_loads: FourCorner[float]
    ) -> FourCorner[TyreAttitude]:
        pass

    @abstractmethod
    def get_lateral_traction(
        self, attitudes: FourCorner[TyreAttitude], required_fx: float
    ) -> FourCorner[float]:
        pass

    @abstractmethod
    def get_longitudinal_traction(
        self, attitudes: FourCorner[TyreAttitude], required_fy: float
    ) -> FourCorner[float]:
        pass
