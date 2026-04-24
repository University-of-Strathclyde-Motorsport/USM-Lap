"""
This module defines the bicycle vehicle model.
"""

from usmlap.model.vehicle_state import Trajectory
from usmlap.utils.datatypes import FourCorner, FrontRear

from ..context import NodeContext
from ..errors import InsufficientTractionError
from .traction_model import TractionModel

PRECISION = 1e-3
MAXIMUM_ITERATIONS = 100


class Bicycle(TractionModel):
    """
    Bicycle vehicle model.
    """

    def lateral_traction(
        self, ctx: NodeContext, trajectory: Trajectory
    ) -> FourCorner[float]:

        resistive_fx = sum(self.resistive_forces(ctx, trajectory.velocity))
        normal_loads = self.normal_loads(ctx, trajectory)
        attitudes = self.get_tyre_attitudes(normal_loads)
        tyres = self.get_tyres(ctx.vehicle)

        fx_max = self.fx_max(tyres, attitudes)
        fy_max = self.fy_max(tyres, attitudes)
        fx = FourCorner(0, 0, resistive_fx / 2, resistive_fx / 2)
        fy = self.fy_available(fx, fx_max, fy_max)

        return fy

    def longitudinal_traction(
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

        body_fz, aero_fz = self.normal_forces(ctx, trajectory.velocity)
        normal_force = self._split_normal_force(ctx, body_fz, aero_fz)

        inertial_lt = self._inertial_load_transfer(ctx, body_fx + inertial_fx)
        aero_lt = self._aero_load_transfer(ctx, aero_fx)

        axle_loads = normal_force + inertial_lt + aero_lt
        return FourCorner(
            0.5 * axle_loads.front,
            0.5 * axle_loads.front,
            0.5 * axle_loads.rear,
            0.5 * axle_loads.rear,
        )

    def _split_normal_force(
        self, ctx: NodeContext, inertial: float, aero: float
    ) -> FrontRear[float]:
        split_inertial = ctx.vehicle.mass_distribution * inertial
        split_aero = ctx.vehicle.aero_distribution * aero
        return split_inertial + split_aero

    def _inertial_load_transfer(
        self, ctx: NodeContext, inertial_fx: float
    ) -> FrontRear[float]:
        cog_height = ctx.vehicle.suspension.centre_of_gravity_height
        wheelbase = ctx.vehicle.suspension.wheelbase
        lt = inertial_fx * (cog_height / wheelbase)
        return FrontRear(-lt, lt)

    def _aero_load_transfer(
        self, ctx: NodeContext, aero_fx: float
    ) -> FrontRear[float]:
        cop_height = ctx.vehicle.aero.centre_of_pressure_height
        wheelbase = ctx.vehicle.suspension.wheelbase
        lt = aero_fx * (cop_height / wheelbase)
        return FrontRear(-lt, lt)

    def _split_traction(
        self, maximum: FourCorner[float], required: float
    ) -> FourCorner[float]:
        available = sum(maximum)
        if required > available:
            raise InsufficientTractionError(required, available)
        saturation = required / available  # Between 0 and 1
        return maximum * saturation
