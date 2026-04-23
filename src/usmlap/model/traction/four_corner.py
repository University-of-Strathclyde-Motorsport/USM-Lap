"""
This module defines the four corner vehicle model.
"""

import math

from usmlap.model.context import NodeContext
from usmlap.model.errors import InsufficientTractionError, WheelLiftError
from usmlap.model.vehicle_state import Trajectory
from usmlap.utils.datatypes import FourCorner, FrontRear
from usmlap.vehicle.tyre import TyreAttitude
from usmlap.vehicle.tyre.tyre_model import TyreModelInterface

from .traction_model import TractionModel

PRECISION = 1e-3
MAXIMUM_ITERATIONS = 100


class FourCornerModel(TractionModel):
    """
    Four corner vehicle model.
    """

    def lateral_traction(
        self, ctx: NodeContext, trajectory: Trajectory
    ) -> float:

        resistive_fx = sum(self.resistive_forces(ctx, trajectory.velocity))
        normal_loads = self.normal_loads(ctx, trajectory)
        if min(normal_loads) < 0:
            raise WheelLiftError(normal_loads, trajectory.ax, trajectory.ay)

        attitudes = FourCorner(
            *(TyreAttitude(normal_load=load) for load in normal_loads)
        )
        tyres = self._tyres(ctx)

        max_rl_fx = tyres.rl.calculate_longitudinal_force(attitudes.rl)
        max_rr_fx = tyres.rr.calculate_longitudinal_force(attitudes.rr)
        required_fx = self._split_traction(
            FourCorner(0, 0, max_rl_fx, max_rr_fx), resistive_fx
        )

        traction = FourCorner(
            *(
                tyre.calculate_lateral_force(attitude, required_fx=fx)
                for tyre, attitude, fx in zip(tyres, attitudes, required_fx)
            )
        )

        return sum(traction)

    def longitudinal_traction(
        self, ctx: NodeContext, trajectory: Trajectory
    ) -> float:
        required_fy = abs(self.required_fy(ctx, trajectory.velocity))

        normal_loads = self.normal_loads(ctx, trajectory)
        if min(normal_loads) < 0:
            raise WheelLiftError(
                normal_loads, ax=trajectory.ax, ay=trajectory.ay
            )

        fl_attitude = TyreAttitude(normal_load=normal_loads.front_left)
        fr_attitude = TyreAttitude(normal_load=normal_loads.front_right)
        rl_attitude = TyreAttitude(normal_load=normal_loads.rear_left)
        rr_attitude = TyreAttitude(normal_load=normal_loads.rear_right)

        front_tyre = ctx.vehicle.tyres.front.tyre_model
        rear_tyre = ctx.vehicle.tyres.rear.tyre_model

        fl_fy = front_tyre.calculate_lateral_force(fl_attitude)
        fr_fy = front_tyre.calculate_lateral_force(fr_attitude)
        front_fy = fl_fy + fr_fy

        rear_fy = max(required_fy - front_fy, 0)
        max_rl_fy = rear_tyre.calculate_lateral_force(rl_attitude)
        max_rr_fy = rear_tyre.calculate_lateral_force(rr_attitude)

        _, _, rl_fy, rr_fy = self._split_traction(
            FourCorner(0, 0, max_rl_fy, max_rr_fy), rear_fy
        )

        rl_fx = rear_tyre.calculate_longitudinal_force(
            rl_attitude, required_fy=rl_fy
        )
        rr_fx = rear_tyre.calculate_longitudinal_force(
            rr_attitude, required_fy=rr_fy
        )

        return rl_fx + rr_fx

    def braking_traction(
        self, ctx: NodeContext, trajectory: Trajectory
    ) -> float:
        required_fy = abs(self.required_fy(ctx, trajectory.velocity))
        normal_loads = self.normal_loads(ctx, trajectory)
        fl_attitude = TyreAttitude(normal_load=normal_loads.front_left)
        fr_attitude = TyreAttitude(normal_load=normal_loads.front_right)
        rl_attitude = TyreAttitude(normal_load=normal_loads.rear_left)
        rr_attitude = TyreAttitude(normal_load=normal_loads.rear_right)

        front_tyre = ctx.vehicle.tyres.front.tyre_model
        rear_tyre = ctx.vehicle.tyres.rear.tyre_model

        max_fl_fy = front_tyre.calculate_lateral_force(fl_attitude)
        max_fr_fy = front_tyre.calculate_lateral_force(fr_attitude)
        max_rl_fy = rear_tyre.calculate_lateral_force(rl_attitude)
        max_rr_fy = rear_tyre.calculate_lateral_force(rr_attitude)
        maximum_fy = FourCorner(max_fl_fy, max_fr_fy, max_rl_fy, max_rr_fy)

        fl_fy, fr_fy, rl_fy, rr_fy = self._split_traction(
            maximum_fy, required_fy
        )

        fl_fx = front_tyre.calculate_longitudinal_force(fl_attitude, fl_fy)
        fr_fx = front_tyre.calculate_longitudinal_force(fr_attitude, fr_fy)
        rl_fx = rear_tyre.calculate_longitudinal_force(rl_attitude, rl_fy)
        rr_fx = rear_tyre.calculate_longitudinal_force(rr_attitude, rr_fy)

        return fl_fx + fr_fx + rl_fx + rr_fx

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

    def _get_next_ax(self, ax: float, axs: list[float]) -> float:
        if len(axs) < 2:
            return ax
        factor = math.exp(-0.05 * (len(axs) - 1))
        return (factor * ax) + ((1 - factor) * axs[-1])

    def _tyres(self, ctx: NodeContext) -> FourCorner[TyreModelInterface]:
        front = ctx.vehicle.tyres.front.tyre_model
        rear = ctx.vehicle.tyres.rear.tyre_model
        return FourCorner(front, front, rear, rear)
