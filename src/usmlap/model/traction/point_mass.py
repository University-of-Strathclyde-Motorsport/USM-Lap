"""
This module defines the point mass vehicle model.
"""

import logging

from usmlap.model.vehicle_state import Trajectory
from usmlap.utils.datatypes import FourCorner

from ..context import NodeContext
from .traction_model import TractionModel

logger = logging.getLogger(__name__)

PRECISION = 1e-2
MAXIMUM_ITERATIONS = 100


class PointMass(TractionModel):
    """
    Point mass vehicle model.
    """

    def lateral_traction(
        self, ctx: NodeContext, trajectory: Trajectory
    ) -> FourCorner[float]:
        resistive_fx = sum(self.resistive_forces(ctx, trajectory.velocity))
        normal_loads = self.normal_loads(ctx, trajectory)
        attitudes = self.get_tyre_attitudes(normal_loads)
        tyres = ctx.vehicle.tyres

        front_fy = self.tyre_model.fy_max(tyres.front, attitudes.front_left)

        rear_fx_max = self.tyre_model.fx_max(tyres.rear, attitudes.rear_left)
        rear_fy_max = self.tyre_model.fy_max(tyres.rear, attitudes.rear_left)
        rear_fy = self.tyre_model.fy(
            fx=resistive_fx / 2, fx_max=rear_fx_max, fy_max=rear_fy_max
        )

        return FourCorner(front_fy, front_fy, rear_fy, rear_fy)

    def longitudinal_traction(
        self, ctx: NodeContext, trajectory: Trajectory
    ) -> FourCorner[float]:
        required_fy = abs(self.required_fy(ctx, trajectory.velocity))
        normal_loads = self.normal_loads(ctx, trajectory)
        attitudes = self.get_tyre_attitudes(normal_loads)
        tyres = ctx.vehicle.tyres

        front_fy = self.tyre_model.fy_max(tyres.front, attitudes.front_left)
        rear_fy = max(required_fy - 2 * front_fy, 0)

        rear_fy_max = self.tyre_model.fy_max(tyres.rear, attitudes.rear_left)
        rear_fx_max = self.tyre_model.fx_max(tyres.rear, attitudes.rear_left)
        rear_traction = self.tyre_model.fx(
            fy=rear_fy / 2, fx_max=rear_fx_max, fy_max=rear_fy_max
        )

        return FourCorner(0, 0, rear_traction, rear_traction)

    def braking_traction(
        self, ctx: NodeContext, trajectory: Trajectory
    ) -> FourCorner[float]:

        required_fy = self.required_fy(ctx, trajectory.velocity)
        normal_loads = self.normal_loads(ctx, trajectory)
        attitudes = self.get_tyre_attitudes(normal_loads)
        tyres = ctx.vehicle.tyres

        front_fx_max = self.tyre_model.fx_max(tyres.front, attitudes.front_left)
        front_fy_max = self.tyre_model.fy_max(tyres.front, attitudes.front_left)
        front_traction = self.tyre_model.fx(
            fy=required_fy / 4, fx_max=front_fx_max, fy_max=front_fy_max
        )

        rear_fx_max = self.tyre_model.fx_max(tyres.rear, attitudes.rear_left)
        rear_fy_max = self.tyre_model.fy_max(tyres.rear, attitudes.rear_left)
        rear_traction = self.tyre_model.fx(
            fy=required_fy / 4, fx_max=rear_fx_max, fy_max=rear_fy_max
        )

        return FourCorner(
            front_traction, front_traction, rear_traction, rear_traction
        )

    def normal_loads(
        self, ctx: NodeContext, trajectory: Trajectory
    ) -> FourCorner[float]:
        normal_force = sum(self.normal_forces(ctx, trajectory.velocity))
        return FourCorner(
            0.25 * normal_force,
            0.25 * normal_force,
            0.25 * normal_force,
            0.25 * normal_force,
        )
