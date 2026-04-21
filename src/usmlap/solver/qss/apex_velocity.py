"""
This module implements the apex solver,
which calculates the theoretical maximum velocity at each node,
assuming zero longitudinal acceleration.
"""

import math
from typing import Optional

from usmlap.model import NodeContext, TractionModel
from usmlap.model.errors import WheelLiftError
from usmlap.model.vehicle_state import VehicleMotion
from usmlap.solver.errors import MaximumIterationsExceededError

PRECISION = 1e-2
MAXIMUM_ITERATIONS = 100

MIN_ERROR_SCALE_FACTOR = 0.1
MAX_ERROR_SCALE_FACTOR = 0.9


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

    velocities: list[float] = [velocity_estimate]

    for _ in range(1, maximum_iterations + 1):
        ay = v_to_ay(v=velocities[-1], curvature=ctx.node.curvature)  # SIGNED
        try:
            motion = VehicleMotion(velocities[-1], ax=0, ay=ay)
            available_fy = vehicle_model.lateral_traction(ctx, motion)
            ay = available_fy / ctx.vehicle.total_mass
            velocities.append(
                ay_to_velocity(ay=ay, curvature=ctx.node.curvature)
            )

        except WheelLiftError as e:
            # TODO: Make this more robust
            scale_factor = 1 - (2 * e.max_wheel_lift) / e.lateral_load_transfer
            scale_factor = max(MIN_ERROR_SCALE_FACTOR, scale_factor)
            scale_factor = min(MAX_ERROR_SCALE_FACTOR, scale_factor)
            v_scale_factor = math.sqrt(scale_factor)
            velocities.append(velocities[-1] * v_scale_factor)
            continue

        if abs(velocities[-1] - velocities[-2]) < precision:
            return velocities[-1]

        if velocities[-1] >= maximum_velocity:
            return maximum_velocity

    raise MaximumIterationsExceededError(
        maximum_iterations, precision, velocities
    )


def _update_velocity_estimate(
    velocity: float, fy_error: float, curvature: float, vehicle_mass: float
) -> float:
    """
    Update the velocity estimate for the next iteration.

    Args:
        velocity (float): The current velocity estimate.
        fy_error (float): The lateral force error.
        curvature (float): The curvature of the track segment.
        vehicle_mass (float): The mass of the vehicle.
    """
    return math.sqrt(velocity**2 + fy_error / (abs(curvature) * vehicle_mass))


def v_to_ay(v: float, curvature: float) -> float:
    return curvature * v**2


def ay_to_velocity(ay: float, curvature: float) -> float:
    return math.sqrt(ay / abs(curvature))
