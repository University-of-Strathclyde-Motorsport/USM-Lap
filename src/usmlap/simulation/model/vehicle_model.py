"""
This module defines the interface for vehicle models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from usmlap.simulation import Environment
from usmlap.simulation.vehicle_state import FullVehicleState, StateVariables
from usmlap.track import TrackNode
from usmlap.utils.datatypes import FourCorner
from usmlap.vehicle import Vehicle
from usmlap.vehicle.aero import AeroAttitude
from usmlap.vehicle.tyre import TyreAttitude

from ..lambda_coefficients import LambdaCoefficients
from .powertrain import PowertrainModelInterface, SingleMotorPowertrain


@dataclass
class VehicleModelInterface(ABC):
    """
    Abstract base class for vehicle models.
    """

    vehicle: Vehicle
    environment: Environment
    lambdas: LambdaCoefficients
    powertrain: PowertrainModelInterface = SingleMotorPowertrain()

    def weight(self) -> float:
        return self.vehicle.total_mass * self.environment.gravity

    def centripetal_force(self, node: TrackNode, velocity: float) -> float:
        return self.vehicle.total_mass * node.curvature * velocity**2

    def aero_attitude(self, velocity: float) -> AeroAttitude:
        return AeroAttitude(
            velocity=velocity, air_density=self.environment.air_density
        )

    def downforce(self, velocity: float) -> float:
        aero_attitude = self.aero_attitude(velocity)
        return self.vehicle.aero.get_downforce(aero_attitude)

    def drag(self, velocity: float) -> float:
        aero_attitude = self.aero_attitude(velocity)
        return self.vehicle.aero.get_drag(aero_attitude)

    def resistive_fx(self, node: TrackNode, velocity: float) -> float:
        weight = self.weight()
        drag = self.drag(velocity)
        return drag + node.z_to_x(weight)

    def required_fy(self, node: TrackNode, velocity: float) -> float:
        weight = self.weight()
        centripetal_force = self.centripetal_force(node, velocity)
        return node.y_to_y(centripetal_force) - node.z_to_y(weight)

    @abstractmethod
    def lateral_traction_limit(
        self, state: StateVariables, node: TrackNode, velocity: float
    ) -> float: ...

    @abstractmethod
    def traction_limited_acceleration(
        self, state: StateVariables, node: TrackNode, velocity: float
    ) -> float: ...

    @abstractmethod
    def traction_limited_braking(
        self, state: StateVariables, node: TrackNode, velocity: float
    ) -> float: ...

    def power_limited_acceleration(
        self, state: StateVariables, node: TrackNode, velocity: float
    ) -> float:

        drive_force = self.powertrain.drive_force(self.vehicle, state, velocity)
        resistive_force = self.resistive_fx(node, velocity)
        net_force = drive_force - resistive_force
        return net_force / self.vehicle.equivalent_mass

    ###############################################
    # Time is running out

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
