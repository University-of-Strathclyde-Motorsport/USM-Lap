"""
This module defines the point mass vehicle model.
"""

import logging

from usmlap.simulation.vehicle_state import StateVariables
from usmlap.track import TrackNode
from usmlap.utils.datatypes import FourCorner
from usmlap.vehicle.tyre import TyreAttitude

from ..errors import InsufficientTractionError
from .vehicle_model import VehicleModelInterface

logger = logging.getLogger(__name__)

PRECISION = 1e-2
MAXIMUM_ITERATIONS = 100


class PointMassVehicleModel(VehicleModelInterface):
    """
    Point mass vehicle model.
    """

    # def get_normal_loads(self, normal_force: float) -> FourCorner[float]:
    #     normal_load = normal_force / 4
    #     return FourCorner((normal_load, normal_load, normal_load, normal_load))

    # def get_tyre_attitudes(
    #     self, normal_loads: FourCorner[float]
    # ) -> FourCorner[TyreAttitude]:
    #     attitudes = [
    #         TyreAttitude(normal_load=normal_load)
    #         for normal_load in normal_loads
    #     ]
    #     return FourCorner(
    #         (attitudes[0], attitudes[1], attitudes[2], attitudes[3])
    #     )

    # def get_lateral_traction(
    #     self, attitudes: FourCorner[TyreAttitude], required_fx: float
    # ) -> FourCorner[float]:
    #     required_fx = required_fx / self.lambdas.longitudinal_grip
    #     front_tyre = self.vehicle.tyres.front.tyre_model.calculate_lateral_force
    #     rear_tyre = self.vehicle.tyres.rear.tyre_model.calculate_lateral_force
    #     try:
    #         return FourCorner(
    #             (
    #                 front_tyre(attitudes.front_left, required_fx=0),
    #                 front_tyre(attitudes.front_right, required_fx=0),
    #                 rear_tyre(attitudes.rear_left, required_fx=required_fx / 2),
    #                 rear_tyre(
    #                     attitudes.rear_right, required_fx=required_fx / 2
    #                 ),
    #             )
    #         )
    #     except ValueError:
    #         return FourCorner((0, 0, 0, 0))

    # def get_longitudinal_traction(
    #     self, attitudes: FourCorner[TyreAttitude], required_fy: float
    # ) -> FourCorner[float]:
    #     required_fy = required_fy / self.lambdas.lateral_grip
    #     front_tyre = (
    #         self.vehicle.tyres.front.tyre_model.calculate_longitudinal_force
    #     )
    #     rear_tyre = (
    #         self.vehicle.tyres.rear.tyre_model.calculate_longitudinal_force
    #     )
    #     fy_per_tyre = abs(required_fy / 4)
    #     try:
    #         return FourCorner(
    #             (
    #                 front_tyre(attitudes.front_left, required_fy=fy_per_tyre),
    #                 front_tyre(attitudes.front_right, required_fy=fy_per_tyre),
    #                 rear_tyre(attitudes.rear_left, required_fy=fy_per_tyre),
    #                 rear_tyre(attitudes.rear_right, required_fy=fy_per_tyre),
    #             )
    #         )
    #     except ValueError:
    #         return FourCorner((0, 0, 0, 0))

    # def calculate_acceleration(
    #     self, state_variables: StateVariables, node: TrackNode, velocity: float
    # ) -> float:
    #     vehicle_state = self.resolve_vehicle_state(
    #         state_variables, node, velocity
    #     )
    #     traction_limit = (
    #         vehicle_state.longitudinal_traction.rear_left
    #         + vehicle_state.longitudinal_traction.rear_right
    #     ) * self.lambdas.longitudinal_grip
    #     motor_limit = vehicle_state.motor_force * self.lambdas.motor_torque
    #     drive_limit = min(motor_limit, traction_limit)
    #     net_fx = drive_limit - vehicle_state.resistive_fx
    #     return net_fx / self.vehicle.equivalent_mass

    # def calculate_deceleration(
    #     self, state_variables: StateVariables, node: TrackNode, velocity: float
    # ) -> float:
    #     vehicle_state = self.resolve_vehicle_state(
    #         state_variables, node, velocity
    #     )
    #     traction_limit = (
    #         sum(vehicle_state.longitudinal_traction)
    #         * self.lambdas.longitudinal_grip
    #     )
    #     net_fx = traction_limit + vehicle_state.resistive_fx
    #     return net_fx / self.vehicle.equivalent_mass

    def lateral_traction_limit(
        self, state_variables: StateVariables, node: TrackNode, velocity: float
    ) -> float:
        weight = self.weight()
        centripetal_force = self.centripetal_force(node, velocity)
        downforce = self.downforce(velocity)

        resistive_fx = self.resistive_fx(node, velocity)

        normal_force = (
            node.z_to_z(weight) + node.y_to_z(centripetal_force) + downforce
        )
        # Force is split evenly between all 4 tyres
        tyre_attitude = TyreAttitude(normal_load=normal_force / 4)

        front_tyre = self.vehicle.tyres.front.tyre_model
        front_traction = 2 * front_tyre.calculate_lateral_force(
            tyre_attitude, required_fx=0
        )

        try:
            rear_tyre = self.vehicle.tyres.rear.tyre_model
            rear_traction = 2 * rear_tyre.calculate_lateral_force(
                tyre_attitude, required_fx=resistive_fx / 2
            )
            print(f"{rear_traction=}")
        except ValueError:
            available_traction = 2 * rear_tyre.calculate_longitudinal_force(
                tyre_attitude, required_fy=0
            )
            raise InsufficientTractionError(
                required=resistive_fx, available=available_traction
            )

        traction_limit = front_traction + rear_traction
        return traction_limit

    def traction_limited_acceleration(
        self, state_variables: StateVariables, node: TrackNode, velocity: float
    ) -> float:

        weight = self.weight()
        resistive_fx = self.resistive_fx(node, velocity)
        print(f"{resistive_fx=}")
        centripetal_force = self.centripetal_force(node, velocity)
        required_fy = self.required_fy(node, velocity)
        print(f"{required_fy=}")

        downforce = self.downforce(velocity)
        normal_force = (
            node.z_to_z(weight) + node.y_to_z(centripetal_force) + downforce
        )
        print(f"{normal_force=}")
        tyre_attitude = TyreAttitude(normal_load=normal_force / 4)

        front_tyre = self.vehicle.tyres.front.tyre_model
        rear_tyre = self.vehicle.tyres.rear.tyre_model
        try:
            _ = front_tyre.calculate_longitudinal_force(
                tyre_attitude, abs(required_fy / 4)
            )

            rear_traction = 2 * rear_tyre.calculate_longitudinal_force(
                tyre_attitude, abs(required_fy / 4)
            )
            print(f"{rear_traction=}")
        except ValueError:
            front_traction = 2 * front_tyre.calculate_lateral_force(
                tyre_attitude, 0
            )
            rear_traction = 2 * rear_tyre.calculate_lateral_force(
                tyre_attitude, 0
            )
            available_traction = front_traction + rear_traction
            raise InsufficientTractionError(
                required=abs(required_fy), available=available_traction
            )

        net_force = rear_traction - resistive_fx
        return net_force / self.vehicle.equivalent_mass

    def traction_limited_braking(
        self, state_variables: StateVariables, node: TrackNode, velocity: float
    ) -> float:

        weight = self.weight()
        resistive_fx = self.resistive_fx(node, velocity)
        centripetal_force = self.centripetal_force(node, velocity)
        required_fy = self.required_fy(node, velocity)

        downforce = self.downforce(velocity)
        normal_force = (
            node.z_to_z(weight) + node.y_to_z(centripetal_force) + downforce
        )
        tyre_attitude = TyreAttitude(normal_load=normal_force / 4)

        front_tyre = self.vehicle.tyres.front.tyre_model
        rear_tyre = self.vehicle.tyres.rear.tyre_model

        try:
            front_traction = 2 * front_tyre.calculate_longitudinal_force(
                tyre_attitude, abs(required_fy / 4)
            )

            rear_traction = 2 * rear_tyre.calculate_longitudinal_force(
                tyre_attitude, abs(required_fy / 4)
            )
        except ValueError:
            front_traction = 2 * front_tyre.calculate_lateral_force(
                tyre_attitude, 0
            )
            rear_traction = 2 * rear_tyre.calculate_lateral_force(
                tyre_attitude, 0
            )
            available_traction = front_traction + rear_traction
            raise InsufficientTractionError(
                required=abs(required_fy), available=available_traction
            )

        net_force = -front_traction - rear_traction - resistive_fx
        return net_force / self.vehicle.equivalent_mass
