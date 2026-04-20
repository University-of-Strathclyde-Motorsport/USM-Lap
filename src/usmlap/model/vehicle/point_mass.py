"""
This module defines the point mass vehicle model.
"""

import logging

from usmlap.model.vehicle_state import VehicleMotion
from usmlap.utils.datatypes import FourCorner
from usmlap.vehicle.tyre import TyreAttitude

from ..context import NodeContext
from .interface import VehicleModelInterface

logger = logging.getLogger(__name__)

PRECISION = 1e-2
MAXIMUM_ITERATIONS = 100


class PointMass(VehicleModelInterface):
    """
    Point mass vehicle model.
    """

    def lateral_traction(
        self, ctx: NodeContext, motion: VehicleMotion
    ) -> float:
        resistive_fx = sum(self.resistive_forces(ctx, motion.velocity))
        normal_loads = self.normal_loads(ctx, motion)

        tyre_attitude = TyreAttitude(normal_load=normal_loads.front_left)

        front_tyre = ctx.vehicle.tyres.front.tyre_model.calculate_lateral_force
        front_traction = front_tyre(tyre_attitude, required_fx=0)

        rear_tyre = ctx.vehicle.tyres.rear.tyre_model.calculate_lateral_force
        rear_traction = rear_tyre(tyre_attitude, required_fx=resistive_fx / 2)

        return 2 * (front_traction + rear_traction)

    def longitudinal_traction(
        self, ctx: NodeContext, motion: VehicleMotion
    ) -> float:
        required_fy = abs(self.required_fy(ctx, motion.velocity))
        normal_loads = self.normal_loads(ctx, motion)

        tyre_attitude = TyreAttitude(normal_load=normal_loads.front_left)

        front_tyre = ctx.vehicle.tyres.front.tyre_model
        front_fy = 2 * front_tyre.calculate_lateral_force(tyre_attitude)

        rear_fy = max(required_fy - front_fy, 0)
        rear_tyre = ctx.vehicle.tyres.rear.tyre_model
        rear_traction = 2 * rear_tyre.calculate_longitudinal_force(
            tyre_attitude, required_fy=rear_fy / 2
        )
        return rear_traction

    def braking_traction(
        self, ctx: NodeContext, motion: VehicleMotion
    ) -> float:

        required_fy = self.required_fy(ctx, motion.velocity)
        normal_loads = self.normal_loads(ctx, motion)

        tyre_attitude = TyreAttitude(normal_load=normal_loads.front_left)

        front_tyre = ctx.vehicle.tyres.front.tyre_model
        front_traction = 2 * front_tyre.calculate_longitudinal_force(
            tyre_attitude, required_fy=required_fy / 4
        )

        rear_tyre = ctx.vehicle.tyres.rear.tyre_model
        rear_traction = 2 * rear_tyre.calculate_longitudinal_force(
            tyre_attitude, required_fy=required_fy / 4
        )
        return front_traction + rear_traction

    def normal_loads(
        self, ctx: NodeContext, motion: VehicleMotion
    ) -> FourCorner[float]:
        normal_force = sum(self.normal_forces(ctx, motion.velocity))
        return FourCorner(
            0.25 * normal_force,
            0.25 * normal_force,
            0.25 * normal_force,
            0.25 * normal_force,
        )
