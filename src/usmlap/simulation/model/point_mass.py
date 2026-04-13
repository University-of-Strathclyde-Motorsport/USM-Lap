"""
This module defines the point mass vehicle model.
"""

import logging

from usmlap.utils.datatypes import FourCorner
from usmlap.vehicle.tyre import TyreAttitude

from .context import Context
from .vehicle_model import VehicleModelInterface

logger = logging.getLogger(__name__)

PRECISION = 1e-2
MAXIMUM_ITERATIONS = 100


class PointMassVehicleModel(VehicleModelInterface):
    """
    Point mass vehicle model.
    """

    def lateral_traction_limit(self, ctx: Context, velocity: float) -> float:

        resistive_fx = sum(self.resistive_forces(ctx, velocity))
        normal_force = self._get_normal_force(ctx, velocity)

        tyre_attitude = TyreAttitude(normal_load=normal_force / 4)

        front_tyre = ctx.vehicle.tyres.front.tyre_model.calculate_lateral_force
        front_traction = front_tyre(tyre_attitude, required_fx=0)

        rear_tyre = ctx.vehicle.tyres.rear.tyre_model.calculate_lateral_force
        rear_traction = rear_tyre(tyre_attitude, required_fx=resistive_fx / 2)

        return 2 * (front_traction + rear_traction)

    def traction_limited_acceleration(
        self, ctx: Context, velocity: float
    ) -> float:

        resistive_fx = sum(self.resistive_forces(ctx, velocity))
        required_fy = self.required_fy(ctx, velocity)
        normal_force = self._get_normal_force(ctx, velocity)

        tyre_attitude = TyreAttitude(normal_load=normal_force / 4)

        front_tyre = ctx.vehicle.tyres.front.tyre_model
        front_fy = 2 * front_tyre.calculate_lateral_force(tyre_attitude)

        rear_fy = max(required_fy - front_fy, 0)
        rear_tyre = ctx.vehicle.tyres.rear.tyre_model
        rear_traction = 2 * rear_tyre.calculate_longitudinal_force(
            tyre_attitude, required_fy=rear_fy / 2
        )

        net_force = rear_traction - resistive_fx
        return net_force / ctx.vehicle.equivalent_mass

    def traction_limited_braking(self, ctx: Context, velocity: float) -> float:

        resistive_fx = sum(self.resistive_forces(ctx, velocity))
        required_fy = self.required_fy(ctx, velocity)
        normal_force = self._get_normal_force(ctx, velocity)

        tyre_attitude = TyreAttitude(normal_load=normal_force / 4)

        front_tyre = ctx.vehicle.tyres.front.tyre_model
        front_traction = 2 * front_tyre.calculate_longitudinal_force(
            tyre_attitude, required_fy=required_fy / 4
        )

        rear_tyre = ctx.vehicle.tyres.rear.tyre_model
        rear_traction = 2 * rear_tyre.calculate_longitudinal_force(
            tyre_attitude, required_fy=required_fy / 4
        )

        net_fx = front_traction + rear_traction + resistive_fx
        return net_fx / ctx.vehicle.equivalent_mass

    def _get_normal_force(self, ctx: Context, velocity: float) -> float:
        return sum(self.normal_forces(ctx, velocity))

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
        self,
        ctx: Context,
        attitudes: FourCorner[TyreAttitude],
        required_fx: float,
    ) -> FourCorner[float]:
        front_tyre = ctx.vehicle.tyres.front.tyre_model.calculate_lateral_force
        rear_tyre = ctx.vehicle.tyres.rear.tyre_model.calculate_lateral_force
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
        self,
        ctx: Context,
        attitudes: FourCorner[TyreAttitude],
        required_fy: float,
    ) -> FourCorner[float]:
        front_tyre = (
            ctx.vehicle.tyres.front.tyre_model.calculate_longitudinal_force
        )
        rear_tyre = (
            ctx.vehicle.tyres.rear.tyre_model.calculate_longitudinal_force
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
