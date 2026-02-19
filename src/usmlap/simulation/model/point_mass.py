"""
This module defines the point mass vehicle model.
"""

import math

from usmlap.simulation.vehicle_state import StateVariables
from usmlap.track.mesh import TrackNode
from usmlap.utils.datatypes import FourCorner
from usmlap.vehicle.tyre.tyre_model import TyreAttitude

from .vehicle_model import VehicleModelInterface


class PointMassVehicleModel(VehicleModelInterface):
    """
    Point mass vehicle model.
    """

    def get_normal_loads(self, normal_force: float) -> FourCorner[float]:
        normal_load = normal_force / 4
        return FourCorner((normal_load, normal_load, normal_load, normal_load))

    def get_tyre_attitudes(
        self, normal_loads: FourCorner[float]
    ) -> FourCorner[TyreAttitude]:
        attitudes = [
            TyreAttitude(normal_load=normal_load)
            for normal_load in normal_loads
        ]
        return FourCorner(
            (attitudes[0], attitudes[1], attitudes[2], attitudes[3])
        )

    def get_lateral_traction(
        self, attitudes: FourCorner[TyreAttitude], required_fx: float
    ) -> FourCorner[float]:
        front_tyre = self.vehicle.tyres.front.tyre_model.calculate_lateral_force
        rear_tyre = self.vehicle.tyres.rear.tyre_model.calculate_lateral_force
        try:
            return FourCorner(
                (
                    front_tyre(attitudes.front_left, required_fx=0),
                    front_tyre(attitudes.front_right, required_fx=0),
                    rear_tyre(attitudes.rear_left, required_fx=required_fx / 2),
                    rear_tyre(
                        attitudes.rear_right, required_fx=required_fx / 2
                    ),
                )
            )
        except ValueError:
            return FourCorner((0, 0, 0, 0))

    def get_longitudinal_traction(
        self, attitudes: FourCorner[TyreAttitude], required_fy: float
    ) -> FourCorner[float]:
        front_tyre = (
            self.vehicle.tyres.front.tyre_model.calculate_longitudinal_force
        )
        rear_tyre = (
            self.vehicle.tyres.rear.tyre_model.calculate_longitudinal_force
        )
        fy_per_tyre = abs(required_fy / 4)
        try:
            return FourCorner(
                (
                    front_tyre(attitudes.front_left, required_fy=fy_per_tyre),
                    front_tyre(attitudes.front_right, required_fy=fy_per_tyre),
                    rear_tyre(attitudes.rear_left, required_fy=fy_per_tyre),
                    rear_tyre(attitudes.rear_right, required_fy=fy_per_tyre),
                )
            )
        except ValueError:
            return FourCorner((0, 0, 0, 0))

    def lateral_vehicle_model(
        self, state_variables: StateVariables, node: TrackNode
    ) -> float:
        velocity = self.vehicle.maximum_velocity
        if node.curvature == 0:
            return velocity

        i = 0
        while i < 10000:
            i += 1
            vehicle_state = self.resolve_vehicle_state(
                state_variables, node, velocity
            )
            try:
                available_fy = vehicle_state.total_lateral_traction
            except ValueError:
                available_fy = 0

            if available_fy < abs(vehicle_state.required_fy):
                net_force = available_fy - node.z_to_y(vehicle_state.weight)
                ay = net_force / self.vehicle.total_mass
                velocity = math.sqrt(ay / abs(node.curvature)) - 0.001
            else:
                break

        return velocity

    def calculate_acceleration(
        self, state_variables: StateVariables, node: TrackNode, velocity: float
    ) -> float:
        vehicle_state = self.resolve_vehicle_state(
            state_variables, node, velocity
        )
        traction_limit = (
            vehicle_state.longitudinal_traction.rear_left
            + vehicle_state.longitudinal_traction.rear_right
        )
        motor_limit = vehicle_state.motor_force
        drive_limit = min(motor_limit, traction_limit)
        net_fx = drive_limit - vehicle_state.resistive_fx
        return net_fx / self.vehicle.equivalent_mass

    def calculate_deceleration(
        self, state_variables: StateVariables, node: TrackNode, velocity: float
    ) -> float:
        vehicle_state = self.resolve_vehicle_state(
            state_variables, node, velocity
        )
        traction_limit = sum(vehicle_state.longitudinal_traction)
        net_fx = traction_limit + vehicle_state.resistive_fx
        return net_fx / self.vehicle.equivalent_mass
