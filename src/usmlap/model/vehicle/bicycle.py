"""
This module defines the bicycle vehicle model.
"""

import math

from usmlap.utils.datatypes import FourCorner, FrontRear
from usmlap.vehicle.tyre import TyreAttitude

from ..context import NodeContext
from ..errors import InsufficientTractionError
from .interface import VehicleModelInterface

PRECISION = 1e-3
MAXIMUM_ITERATIONS = 100


class Bicycle(VehicleModelInterface):
    """
    Bicycle vehicle model.
    """

    def lateral_traction(
        self, ctx: NodeContext, velocity: float, ax: float, ay: float
    ) -> float:

        resistive_fx = sum(self.resistive_forces(ctx, velocity))
        normal_loads = self.normal_loads(ctx, velocity, ax=ax, ay=ay)

        front_tyre = ctx.vehicle.tyres.front.tyre_model
        front_attitude = TyreAttitude(normal_load=normal_loads.front_left)
        front_traction = 2 * front_tyre.calculate_lateral_force(front_attitude)

        rear_tyre = ctx.vehicle.tyres.rear.tyre_model
        rear_attitude = TyreAttitude(normal_load=normal_loads.rear_left)
        rear_traction = 2 * rear_tyre.calculate_lateral_force(
            rear_attitude, required_fx=resistive_fx / 2
        )

        return front_traction + rear_traction

    def longitudinal_traction(
        self, ctx: NodeContext, velocity: float, ax: float, ay: float
    ) -> float:
        required_fy = abs(self.required_fy(ctx, velocity))

        normal_loads = self.normal_loads(ctx, velocity, ax, ay=ay)

        front_tyre = ctx.vehicle.tyres.front.tyre_model
        front_attitude = TyreAttitude(normal_load=normal_loads.front_left)
        front_fy = 2 * front_tyre.calculate_lateral_force(front_attitude)

        rear_fy = max(required_fy - front_fy, 0)
        rear_tyre = ctx.vehicle.tyres.rear.tyre_model
        rear_attitude = TyreAttitude(normal_load=normal_loads.rear_left)
        rear_traction = 2 * rear_tyre.calculate_longitudinal_force(
            rear_attitude, required_fy=rear_fy / 2
        )

        return rear_traction

    def braking_traction(
        self, ctx: NodeContext, velocity: float, ax: float, ay: float
    ) -> float:
        required_fy = abs(self.required_fy(ctx, velocity))

        normal_loads = self.normal_loads(ctx, velocity, -ax, ay=ay)

        front_tyre = ctx.vehicle.tyres.front.tyre_model
        front_attitude = TyreAttitude(normal_load=normal_loads.front_left)
        rear_tyre = ctx.vehicle.tyres.rear.tyre_model
        rear_attitude = TyreAttitude(normal_load=normal_loads.rear_left)

        maximum_front_fy = 2 * front_tyre.calculate_lateral_force(
            front_attitude
        )
        maximum_rear_fy = 2 * rear_tyre.calculate_lateral_force(rear_attitude)

        front_fy, rear_fy = self._determine_fy_split(
            FrontRear(maximum_front_fy, maximum_rear_fy), required_fy
        )

        front_traction = 2 * front_tyre.calculate_longitudinal_force(
            front_attitude, required_fy=front_fy / 2
        )

        rear_traction = 2 * rear_tyre.calculate_longitudinal_force(
            rear_attitude, required_fy=rear_fy / 2
        )

        return front_traction + rear_traction

    def normal_loads(
        self, ctx: NodeContext, velocity: float, ax: float, ay: float
    ) -> FourCorner[float]:
        body_fx, aero_fx = self.resistive_forces(ctx, velocity)
        inertial_fx = ctx.vehicle.total_mass * ax

        body_fz, aero_fz = self.normal_forces(ctx, velocity)
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

    def _determine_fy_split(
        self, maximum_fy: FrontRear[float], required_fy: float
    ) -> FrontRear[float]:

        if sum(maximum_fy) < required_fy:
            raise InsufficientTractionError(required_fy, sum(maximum_fy))
        elif maximum_fy.front <= required_fy / 2:
            front_fy = maximum_fy.front
            rear_fy = required_fy - front_fy
        elif maximum_fy.rear <= required_fy / 2:
            rear_fy = maximum_fy.rear
            front_fy = required_fy - rear_fy
        else:
            front_fy = required_fy / 2
            rear_fy = required_fy / 2

        return FrontRear(front_fy, rear_fy)

    def _get_next_ax(self, ax: float, axs: list[float]) -> float:
        if len(axs) < 2:
            return ax
        factor = math.exp(-0.1 * len(axs))
        return (factor * ax) + ((1 - factor) * axs[-1])
