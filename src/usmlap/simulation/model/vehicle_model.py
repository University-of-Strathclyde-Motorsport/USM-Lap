"""
This module defines the interface for vehicle models.
"""

from abc import ABC, abstractmethod
import math
from vehicle.vehicle import Vehicle
from vehicle.aero import AeroAttitude
from simulation.environment import Environment
from track.mesh import Node
from pydantic import BaseModel
from datatypes import Vector3


class VehicleState(BaseModel):
    """
    The state of the vehicle at a point.
    """

    velocity: float
    ax: float = 0


class VehicleModelInterface(ABC):
    """
    Abstract base class for vehicle models.
    """

    vehicle: Vehicle
    environment: Environment

    def __init__(self, vehicle: Vehicle, environment: Environment) -> None:
        self.vehicle = vehicle
        self.environment = environment

    @property
    def weight(self) -> float:
        return self.vehicle.total_mass * self.environment.gravity

    def weight_x(self, node: Node) -> float:
        return self.weight * math.sin(node.inclination)

    def weight_y(self, node: Node) -> float:
        return self.weight * math.sin(node.banking)

    def weight_z(self, node: Node) -> float:
        return self.weight * math.cos(node.banking) * math.cos(node.inclination)

    def weight_array(self, node: Node) -> Vector3:
        weight = self.vehicle.total_mass * self.environment.gravity
        return Vector3(z=weight)

    def _centripetal_force(
        self, vehicle_state: VehicleState, node: Node
    ) -> float:
        return (
            self.vehicle.total_mass * vehicle_state.velocity**2 * node.curvature
        )

    def centripetal_force_y(
        self, vehicle_state: VehicleState, node: Node
    ) -> float:
        return self._centripetal_force(vehicle_state, node) * math.cos(
            node.banking
        )

    def centripetal_force_z(
        self, vehicle_state: VehicleState, node: Node
    ) -> float:
        return self._centripetal_force(vehicle_state, node) * math.sin(
            node.banking
        )

    def downforce(self, vehicle_state: VehicleState) -> float:
        aero_attitude = AeroAttitude(
            velocity=vehicle_state.velocity,
            air_density=self.environment.air_density,
        )
        return self.vehicle.aero.get_downforce(aero_attitude)

    def drag(self, vehicle_state: VehicleState) -> float:
        aero_attitude = AeroAttitude(
            velocity=vehicle_state.velocity,
            air_density=self.environment.air_density,
        )
        return self.vehicle.aero.get_drag(aero_attitude)

    def normal_force(self, vehicle_state: VehicleState, node: Node) -> float:
        weight = self.weight_z(node)
        centripetal_force = self.centripetal_force_z(vehicle_state, node)
        downforce = self.downforce(vehicle_state)
        return weight + centripetal_force + downforce

    def resistive_fx(self, vehicle_state: VehicleState, node: Node) -> float:
        return self.drag(vehicle_state) + self.weight_x(node)

    def required_fy(self, vehicle_state: VehicleState, node: Node) -> float:
        centripetal_force = self.centripetal_force_y(vehicle_state, node)
        weight = self.weight_y(node)
        return centripetal_force + weight

    def motor_force(self, vehicle_state: VehicleState) -> float:
        motor_speed = self.vehicle.velocity_to_motor_speed(
            vehicle_state.velocity
        )
        motor_torque = self.vehicle.powertrain.get_motor_torque(
            state_of_charge=1,  # TODO
            current=self.vehicle.powertrain.accumulator.maximum_discharge_current,
            motor_speed=motor_speed,
        )
        motor_force = self.vehicle.motor_torque_to_drive_force(motor_torque)
        return motor_force

    @abstractmethod
    def lateral_vehicle_model(self, node: Node) -> VehicleState:
        pass

    @abstractmethod
    def calculate_acceleration(
        self, vehicle_state: VehicleState, node: Node
    ) -> float:
        pass

    @abstractmethod
    def calculate_decceleration(
        self, vehicle_state: VehicleState, node: Node
    ) -> float:
        pass
