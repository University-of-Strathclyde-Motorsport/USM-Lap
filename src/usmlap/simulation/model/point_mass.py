"""
This module defines the point mass vehicle model.
"""

import logging

from usmlap.simulation.vehicle_state import StateVariables
from usmlap.track import TrackNode
from usmlap.utils.datatypes import FourCorner
from usmlap.vehicle.tyre import TyreAttitude

from .vehicle_model import VehicleModelInterface

logger = logging.getLogger(__name__)

PRECISION = 1e-2
MAXIMUM_ITERATIONS = 100


class PointMassVehicleModel(VehicleModelInterface):
    """
    Point mass vehicle model.
    """

    def lateral_traction_limit(
        self, state: StateVariables, node: TrackNode, velocity: float
    ) -> float:
        resistive_fx = self.resistive_fx(node, velocity)

        weight = self.weight()
        centripetal_force = self.centripetal_force(node, velocity)
        downforce = self.downforce(velocity)
        normal_force = (
            node.z_to_z(weight) + node.y_to_z(centripetal_force) + downforce
        )

        tyre_attitude = TyreAttitude(normal_load=normal_force / 4)

        front_tyre = self.vehicle.tyres.front.tyre_model.calculate_lateral_force
        front_traction = front_tyre(tyre_attitude, required_fx=0)

        rear_tyre = self.vehicle.tyres.rear.tyre_model.calculate_lateral_force
        rear_traction = rear_tyre(tyre_attitude, required_fx=resistive_fx / 2)

        return 2 * (front_traction + rear_traction)

    def traction_limited_acceleration(
        self, state: StateVariables, node: TrackNode, velocity: float
    ) -> float:

        required_fy = self.required_fy(node, velocity)

        weight = self.weight()
        centripetal_force = self.centripetal_force(node, velocity)
        downforce = self.downforce(velocity)
        normal_force = (
            node.z_to_z(weight) + node.y_to_z(centripetal_force) + downforce
        )

        tyre_attitude = TyreAttitude(normal_load=normal_force / 4)

        front_tyre = self.vehicle.tyres.front.tyre_model
        front_fy = 2 * front_tyre.calculate_lateral_force(tyre_attitude)

        rear_fy = max(required_fy - front_fy, 0)
        rear_tyre = self.vehicle.tyres.rear.tyre_model
        rear_traction = 2 * rear_tyre.calculate_longitudinal_force(
            tyre_attitude, required_fy=rear_fy / 2
        )

        net_force = rear_traction - self.resistive_fx(node, velocity)
        return net_force / self.vehicle.equivalent_mass

    def traction_limited_braking(
        self, state: StateVariables, node: TrackNode, velocity: float
    ) -> float:

        resistive_fx = self.resistive_fx(node, velocity)

        required_fy = self.required_fy(node, velocity)
        fy_per_tyre = required_fy / 4

        weight = self.weight()
        centripetal_force = self.centripetal_force(node, velocity)
        downforce = self.downforce(velocity)
        normal_force = (
            node.z_to_z(weight) + node.y_to_z(centripetal_force) + downforce
        )

        tyre_attitude = TyreAttitude(normal_load=normal_force / 4)

        front_tyre = self.vehicle.tyres.front.tyre_model
        front_traction = 2 * front_tyre.calculate_longitudinal_force(
            tyre_attitude, required_fy=fy_per_tyre
        )

        rear_tyre = self.vehicle.tyres.rear.tyre_model
        rear_traction = 2 * rear_tyre.calculate_longitudinal_force(
            tyre_attitude, required_fy=fy_per_tyre
        )

        net_fx = front_traction + rear_traction + resistive_fx
        return net_fx / self.vehicle.equivalent_mass

    #########################################################
    # Marked for death

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
        required_fx = required_fx / self.lambdas.longitudinal_grip
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
        required_fy = required_fy / self.lambdas.lateral_grip
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
