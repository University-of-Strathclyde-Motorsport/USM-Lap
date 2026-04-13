"""
This module defines the bicycle vehicle model.
"""

from usmlap.model import Context
from usmlap.model.errors import MaximumIterationsExceededError
from usmlap.utils.datatypes import FrontRear
from usmlap.vehicle.tyre import TyreAttitude

from .interface import VehicleModelInterface

PRECISION = 1e-3
MAXIMUM_ITERATIONS = 100


class Bicycle(VehicleModelInterface):
    """
    Bicycle vehicle model.
    """

    def lateral_traction_limit(self, ctx: Context, velocity: float) -> float:
        resistive_fx = sum(self.resistive_forces(ctx, velocity))
        normal_force = self._get_normal_force(ctx, velocity, ax=0)

        front_tyre = ctx.vehicle.tyres.front.tyre_model
        front_attitude = TyreAttitude(normal_load=normal_force.front / 2)
        front_traction = 2 * front_tyre.calculate_lateral_force(front_attitude)

        rear_tyre = ctx.vehicle.tyres.rear.tyre_model
        rear_attitude = TyreAttitude(normal_load=normal_force.rear / 2)
        rear_traction = 2 * rear_tyre.calculate_lateral_force(
            rear_attitude, required_fx=resistive_fx / 2
        )

        return front_traction + rear_traction

    def traction_limited_acceleration(
        self, ctx: Context, velocity: float
    ) -> float:
        resistive_fx = sum(self.resistive_forces(ctx, velocity))
        required_fy = self.required_fy(ctx, velocity)
        axs: list[float] = [0]

        for _ in range(MAXIMUM_ITERATIONS):
            normal_force = self._get_normal_force(ctx, velocity, axs[-1])

            front_tyre = ctx.vehicle.tyres.front.tyre_model
            front_attitude = TyreAttitude(normal_load=normal_force.front / 2)
            front_fy = 2 * front_tyre.calculate_lateral_force(front_attitude)

            rear_fy = max(required_fy - front_fy, 0)
            rear_tyre = ctx.vehicle.tyres.rear.tyre_model
            rear_attitude = TyreAttitude(normal_load=normal_force.rear / 2)
            rear_traction = 2 * rear_tyre.calculate_longitudinal_force(
                rear_attitude, required_fy=rear_fy / 2
            )

            net_force = rear_traction - resistive_fx
            axs.append(net_force / ctx.vehicle.equivalent_mass)

            if abs(axs[-1] - axs[-2]) < PRECISION:
                return axs[-1]

        raise MaximumIterationsExceededError(MAXIMUM_ITERATIONS, PRECISION, axs)

    def traction_limited_braking(self, ctx: Context, velocity: float) -> float:
        resistive_fx = sum(self.resistive_forces(ctx, velocity))
        required_fy = self.required_fy(ctx, velocity)
        axs: list[float] = [0]

        for _ in range(MAXIMUM_ITERATIONS):
            normal_force = self._get_normal_force(ctx, velocity, -axs[-1])

            front_tyre = ctx.vehicle.tyres.front.tyre_model
            front_attitude = TyreAttitude(normal_load=normal_force.front / 2)
            front_traction = 2 * front_tyre.calculate_longitudinal_force(
                front_attitude, required_fy=required_fy / 4
            )

            rear_tyre = ctx.vehicle.tyres.rear.tyre_model
            rear_attitude = TyreAttitude(normal_load=normal_force.rear / 2)
            rear_traction = 2 * rear_tyre.calculate_longitudinal_force(
                rear_attitude, required_fy=required_fy / 4
            )

            net_force = front_traction + rear_traction + resistive_fx
            axs.append(net_force / ctx.vehicle.equivalent_mass)

            if abs(axs[-1] - axs[-2]) < PRECISION:
                return axs[-1]

        raise MaximumIterationsExceededError(MAXIMUM_ITERATIONS, PRECISION, axs)

    def _get_normal_force(
        self, ctx: Context, velocity: float, ax: float
    ) -> FrontRear[float]:
        body_fx, aero_fx = self.resistive_forces(ctx, velocity)
        inertial_fx = ctx.vehicle.total_mass * ax

        inertial_fz, aero_fz = self.normal_forces(ctx, velocity)
        normal_force = self._split_normal_force(ctx, inertial_fz, aero_fz)

        inertial_lt = self._inertial_load_transfer(ctx, body_fx + inertial_fx)
        aero_lt = self._aero_load_transfer(ctx, aero_fx)

        return normal_force + inertial_lt + aero_lt

    def _split_normal_force(
        self, ctx: Context, inertial: float, aero: float
    ) -> FrontRear[float]:
        split_inertial = ctx.vehicle.mass_distribution * inertial
        split_aero = ctx.vehicle.aero_distribution * aero
        return split_inertial + split_aero

    def _inertial_load_transfer(
        self, ctx: Context, inertial_fx: float
    ) -> FrontRear[float]:
        cog_height = ctx.vehicle.suspension.centre_of_gravity_height
        wheelbase = ctx.vehicle.suspension.wheelbase
        lt = inertial_fx * (cog_height / wheelbase)
        return FrontRear(-lt, lt)

    def _aero_load_transfer(
        self, ctx: Context, aero_fx: float
    ) -> FrontRear[float]:
        cop_height = ctx.vehicle.aero.centre_of_pressure_height
        wheelbase = ctx.vehicle.suspension.wheelbase
        lt = aero_fx * (cop_height / wheelbase)
        return FrontRear(-lt, lt)
