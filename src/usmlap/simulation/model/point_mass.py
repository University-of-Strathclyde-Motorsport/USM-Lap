"""
This module defines the point mass vehicle model.
"""

import math
from track.mesh import Node
from .vehicle_model import VehicleModelInterface, VehicleState
from vehicle.tyre.tyre_model import TyreAttitude


class PointMassVehicleModel(VehicleModelInterface):
    """
    Point mass vehicle model.
    """

    def normal_load(self, vehicle_state: VehicleState, node: Node) -> float:
        return self.normal_force(vehicle_state, node) / 4

    def tyre_attitude(
        self, vehicle_state: VehicleState, node: Node
    ) -> TyreAttitude:
        return TyreAttitude(normal_load=self.normal_load(vehicle_state, node))

    def lateral_vehicle_model(self, node: Node) -> VehicleState:
        if node.curvature == 0:
            return VehicleState(velocity=self.vehicle.maximum_velocity, ax=0)

        v = self.vehicle.maximum_velocity
        i = 0

        while i < 10000:
            i += 1
            vehicle_state = VehicleState(velocity=v, ax=0)
            try:
                front_tyre_traction = (
                    self.vehicle.tyres.front.tyre_model.calculate_lateral_force(
                        tyre_attitude=self.tyre_attitude(vehicle_state, node),
                        required_fx=0,
                    )
                )
                rear_tyre_traction = (
                    self.vehicle.tyres.front.tyre_model.calculate_lateral_force(
                        tyre_attitude=self.tyre_attitude(vehicle_state, node),
                        required_fx=self.resistive_fx(vehicle_state, node) / 2,
                    )
                )
                available_fy = 2 * (front_tyre_traction + rear_tyre_traction)
            except ValueError:
                available_fy = 0

            if available_fy < abs(self.required_fy(vehicle_state, node)):
                net_force = available_fy - self.weight_y(node)
                ay = net_force / self.vehicle.total_mass
                v = math.sqrt(ay / abs(node.curvature)) - 0.001
            else:
                break

        vehicle_state = VehicleState(velocity=v, ax=0)
        return vehicle_state

    def calculate_acceleration(
        self, vehicle_state: VehicleState, node: Node
    ) -> float:
        tyre_traction = (
            self.vehicle.tyres.front.tyre_model.calculate_longitudinal_force(
                self.tyre_attitude(vehicle_state, node),
                abs(self.required_fy(vehicle_state, node)) / 4,
            )
        )
        traction_limit = tyre_traction * 2
        motor_limit = self.motor_force(vehicle_state)
        drive_limit = min(motor_limit, traction_limit)
        net_fx = drive_limit - self.resistive_fx(vehicle_state, node)
        with open("log.csv", "a") as file:
            file.write(
                f"{vehicle_state.velocity},"
                f"{self.required_fy(vehicle_state, node)},"
                f"{traction_limit},"
                f"{drive_limit},"
                f"{motor_limit},"
                f"{self.resistive_fx(vehicle_state, node)},"
                f"{net_fx}\n"
            )
        # print(
        #     f"Radius: {node.radius:.2f}, "
        #     f"Velocity: {vehicle_state.velocity:.2f}, "
        #     f"Normal: {self.normal_force(vehicle_state, node):.2f}, "
        #     f"Fy: {self.required_fy(vehicle_state, node):.2f}, "
        #     f"Traction: {traction_limit:.2f}, "
        #     f"Drive: {drive_limit:.2f}, "
        #     f"Motor limit: {motor_limit:.2f}, "
        #     f"Resistive: {self.resistive_fx(vehicle_state, node):.2f}, "
        #     f"Net: {net_fx:.2f}"
        # )
        return net_fx / self.vehicle.equivalent_mass

    def calculate_decceleration(
        self, vehicle_state: VehicleState, node: Node
    ) -> float:
        tyre_traction = (
            self.vehicle.tyres.front.tyre_model.calculate_longitudinal_force(
                self.tyre_attitude(vehicle_state, node),
                abs(self.required_fy(vehicle_state, node)) / 4,
            )
        )
        traction_limit = tyre_traction * 4
        net_fx = traction_limit + self.resistive_fx(vehicle_state, node)
        print(
            f"Radius: {node.radius:.2f}, "
            f"Velocity: {vehicle_state.velocity:.2f}, "
            f"Normal: {self.normal_force(vehicle_state, node):.2f}, "
            f"Fy: {self.required_fy(vehicle_state, node):.2f}, "
            f"Traction: {traction_limit:.2f}, "
            f"Resistive: {self.resistive_fx(vehicle_state, node):.2f}, "
            f"Net: {net_fx:.2f}"
        )
        return net_fx / self.vehicle.equivalent_mass
