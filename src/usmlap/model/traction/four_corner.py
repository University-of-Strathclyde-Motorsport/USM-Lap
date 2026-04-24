"""
This module defines the four corner vehicle model.
"""

from usmlap.model.context import NodeContext
from usmlap.model.errors import InsufficientTractionError, WheelLiftError
from usmlap.model.vehicle_state import Trajectory
from usmlap.utils.datatypes import FourCorner, FrontRear

from .traction_model import TractionModel

PRECISION = 1e-3
MAXIMUM_ITERATIONS = 100


class FourCornerModel(TractionModel):
    """
    Four corner vehicle model.
    """

    def lateral_traction(
        self, ctx: NodeContext, trajectory: Trajectory
    ) -> FourCorner[float]:

        resistive_fx = sum(self.resistive_forces(ctx, trajectory.velocity))
        normal_loads = self.normal_loads(ctx, trajectory)
        if min(normal_loads) < 0:
            raise WheelLiftError(normal_loads, trajectory.ax, trajectory.ay)

        attitudes = self.get_tyre_attitudes(normal_loads)
        tyres = self.get_tyres(ctx.vehicle)

        fx_max = self.fx_max(tyres, attitudes)
        fy_max = self.fy_max(tyres, attitudes)
        fx = self._split_traction(
            FourCorner(0, 0, fx_max.rear_left, fx_max.rear_right), resistive_fx
        )
        fy = self.fy_available(fx, fx_max, fy_max)

        return fy

    def longitudinal_traction(
        self, ctx: NodeContext, trajectory: Trajectory
    ) -> FourCorner[float]:
        required_fy = abs(self.required_fy(ctx, trajectory.velocity))

        normal_loads = self.normal_loads(ctx, trajectory)
        if min(normal_loads) < 0:
            raise WheelLiftError(
                normal_loads, ax=trajectory.ax, ay=trajectory.ay
            )

        attitudes = self.get_tyre_attitudes(normal_loads)
        tyres = self.get_tyres(ctx.vehicle)

        fx_max = self.fx_max(tyres, attitudes)
        fy_max = self.fy_max(tyres, attitudes)
        fy = self._split_traction(fy_max, required_fy)
        fx = self.fx_available(fy, fx_max, fy_max)

        return FourCorner(0, 0, fx.rear_left, fx.rear_right)

    def braking_traction(
        self, ctx: NodeContext, trajectory: Trajectory
    ) -> FourCorner[float]:
        required_fy = abs(self.required_fy(ctx, trajectory.velocity))
        normal_loads = self.normal_loads(ctx, trajectory)
        attitudes = self.get_tyre_attitudes(normal_loads)
        tyres = self.get_tyres(ctx.vehicle)

        fx_max = self.fx_max(tyres, attitudes)
        fy_max = self.fy_max(tyres, attitudes)
        fy = self._split_traction(fy_max, required_fy)
        fx = self.fx_available(fy, fx_max, fy_max)

        return fx

    def normal_loads(
        self, ctx: NodeContext, trajectory: Trajectory
    ) -> FourCorner[float]:
        body_fx, aero_fx = self.resistive_forces(ctx, trajectory.velocity)
        inertial_fx = ctx.vehicle.total_mass * trajectory.ax

        inertial_fy = ctx.vehicle.total_mass * trajectory.ay

        body_fz, aero_fz = self.normal_forces(ctx, trajectory.velocity)
        normal_force = self._split_normal_force(ctx, body_fz, aero_fz)

        inertial_lt_fx = self._inertial_lt_fx(ctx, body_fx + inertial_fx)
        aero_lt_fx = self._aero_lt_fx(ctx, aero_fx)

        inertial_lt_fy = self._inertial_lt_fy(ctx, inertial_fy)

        return normal_force + inertial_lt_fx + aero_lt_fx + inertial_lt_fy

    def _split_normal_force(
        self, ctx: NodeContext, inertial: float, aero: float
    ) -> FourCorner[float]:
        split_inertial = ctx.vehicle.mass_distribution * inertial
        split_aero = ctx.vehicle.aero_distribution * aero
        axle_total = split_inertial + split_aero
        return FourCorner(
            0.5 * axle_total.front,
            0.5 * axle_total.front,
            0.5 * axle_total.rear,
            0.5 * axle_total.rear,
        )

    def _inertial_lt_fx(
        self, ctx: NodeContext, inertial_fx: float
    ) -> FourCorner[float]:

        cog_height = ctx.vehicle.suspension.centre_of_gravity_height
        wheelbase = ctx.vehicle.suspension.wheelbase
        lt = 0.5 * inertial_fx * (cog_height / wheelbase)
        return FourCorner(-lt, -lt, lt, lt)

    def _aero_lt_fx(
        self, ctx: NodeContext, aero_fx: float
    ) -> FourCorner[float]:
        cop_height = ctx.vehicle.aero.centre_of_pressure_height
        wheelbase = ctx.vehicle.suspension.wheelbase
        lt = 0.5 * aero_fx * (cop_height / wheelbase)
        return FourCorner(-lt, -lt, lt, lt)

    def _lateral_load_transfer_distribution(self) -> FrontRear[float]:
        return FrontRear(0.5, 0.5)

    def _inertial_lt_fy(
        self, ctx: NodeContext, inertial_fy: float
    ) -> FourCorner[float]:

        cog_height = ctx.vehicle.suspension.centre_of_gravity_height
        front_track = ctx.vehicle.suspension.front.track_width
        rear_track = ctx.vehicle.suspension.rear.track_width
        avg_track = 0.5 * (front_track + rear_track)

        total_load_transfer = inertial_fy * (cog_height / avg_track)
        lltd = self._lateral_load_transfer_distribution()
        lt = lltd * total_load_transfer

        return FourCorner(-lt.front, lt.front, -lt.rear, lt.rear)

    def _split_traction(
        self, maximum: FourCorner[float], required: float
    ) -> FourCorner[float]:
        available = sum(maximum)
        if required > available:
            raise InsufficientTractionError(required, available)
        saturation = required / available  # Between 0 and 1
        return maximum * saturation
