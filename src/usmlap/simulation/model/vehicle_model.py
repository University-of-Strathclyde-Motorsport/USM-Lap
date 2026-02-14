"""
This module defines the interface for vehicle models.
"""

from abc import ABC, abstractmethod

from simulation.environment import Environment
from simulation.vehicle_state import FullVehicleState, StateVariables
from track.mesh import TrackNode
from utils.datatypes import FourCorner
from vehicle.aero import AeroAttitude
from vehicle.tyre.tyre_model import TyreAttitude
from vehicle.vehicle import Vehicle


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
        self, state_variables: StateVariables, node: TrackNode, velocity: float
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
        vehicle = self.vehicle

        weight = vehicle.total_mass * self.environment.gravity
        centripetal_force = vehicle.total_mass * velocity**2 * node.curvature

        aero_attitude = AeroAttitude(
            velocity=velocity, air_density=self.environment.air_density
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

        motor_speed = vehicle.velocity_to_motor_speed(velocity)
        motor_torque = vehicle.powertrain.get_motor_torque(
            state_of_charge=state_variables.state_of_charge,
            motor_speed=motor_speed,
        )
        motor_power = motor_speed * motor_torque
        accumulator_power = vehicle.powertrain.motor_to_accumulator_power(
            motor_power
        )
        motor_force = vehicle.motor_torque_to_drive_force(motor_torque)

        return FullVehicleState(
            weight=weight,
            centripetal_force=centripetal_force,
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
            motor_power=motor_power,
            accumulator_power=accumulator_power,
            motor_force=motor_force,
        )

    @abstractmethod
    def lateral_vehicle_model(
        self, state_variables: StateVariables, node: TrackNode
    ) -> float:
        """
        Calculate the lateral-traction-limited velocity at a node.

        This is the maximum velocity that the vehicle can travel at
        while maintaining lateral traction with no longitudinal acceleration.

        Args:
            node (TrackNode): The track node to evaluate.

        Returns:
            velocity (float): The lateral traction limited velocity.
        """
        pass

    @abstractmethod
    def calculate_acceleration(
        self, state_variables: StateVariables, node: TrackNode, velocity: float
    ) -> float:
        pass

    @abstractmethod
    def calculate_deceleration(
        self, state_variables: StateVariables, node: TrackNode, velocity: float
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
