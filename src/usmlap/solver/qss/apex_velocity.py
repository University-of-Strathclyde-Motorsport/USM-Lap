"""
This module implements the apex solver,
which calculates the theoretical maximum velocity at each node,
assuming zero longitudinal acceleration.
"""

import math
from typing import Optional

from usmlap.model import NodeContext, TractionModel
from usmlap.model.errors import WheelLiftError
from usmlap.model.vehicle_state import Trajectory
from usmlap.solver.errors import MaximumIterationsExceededError

PRECISION = 1e-2
MAXIMUM_ITERATIONS = 100

MIN_ERROR_SF = 0.1
MAX_ERROR_SF = 0.9


def solve_apex_velocity(
    vehicle_model: TractionModel,
    ctx: NodeContext,
    velocity_estimate: Optional[float] = None,
    precision: float = PRECISION,
    maximum_iterations: int = MAXIMUM_ITERATIONS,
) -> float:
    """
    Calculate the apex velocity at a node.
    This is the maximum velocity that the vehicle can travel at
    while maintaining lateral traction,
    with zero longitudinal acceleration.

    Args:
        vehicle_model (TractionModel):
            The vehicle model to use.
        ctx (NodeContext): The simulation context.
        velocity_estimate (Optional[float]):
            The initial velocity estimate, used to speed up calculation.
            If unspecified, defaults to the maximum velocity of the vehicle.
        precision (float):
            The maximum error allowed in the calculation.
        maximum_iterations (int):
            The maximum number of iterations to perform before raising an error.
            If high precision is required, this value may need to be increased.

    Returns:
        apex_velocity (float): The apex velocity at the node.

    Raises:
        MaximumIterationsExceededError:
            If the maximum number of iterations is exceeded
            without converging on a solution.
    """

    maximum_velocity = ctx.vehicle.maximum_velocity

    if ctx.node.curvature == 0:
        return maximum_velocity

    if velocity_estimate is None:
        velocity_estimate = maximum_velocity

    velocities: list[float] = []

    trajectory = Trajectory(
        velocity=velocity_estimate, ax=0, curvature=ctx.node.curvature
    )

    for _ in range(1, maximum_iterations + 1):
        velocities.append(trajectory.velocity)
        try:
            available_fy = vehicle_model.lateral_traction(ctx, trajectory)
            ay = available_fy / ctx.vehicle.total_mass
            trajectory.ay = math.copysign(ay, trajectory.curvature)

        except WheelLiftError as e:
            # TODO: Make this more robust
            scale_factor = 1 - (2 * e.max_wheel_lift) / e.lateral_load_transfer
            clamped_scale_factor = min(
                max(scale_factor, MIN_ERROR_SF), MAX_ERROR_SF
            )
            trajectory.ay *= clamped_scale_factor * scale_factor
            continue

        if abs(trajectory.velocity - velocities[-1]) < precision:
            return trajectory.velocity

        if trajectory.velocity >= maximum_velocity:
            return maximum_velocity

    raise MaximumIterationsExceededError(
        maximum_iterations, precision, velocities
    )
