"""
This module implements the acceleration solver,
which calculates the maximum possible acceleration at a node.
"""

import math

from usmlap.model import Context, VehicleModelInterface


def calculate_next_velocity(
    model: VehicleModelInterface, ctx: Context, initial_velocity: float
) -> float:
    """
    Calculate the velocity at the end of a node,
    given the initial velocity at the start of the node.

    Args:
        vehicle_model (VehicleModelInterface): The vehicle model to use.
        state (StateVariables): The vehicle's state variables.
        node (TrackNode): The track node to solve.
        initial_velocity (float): The velocity at the start of the node.

    Returns:
        final_velocity (float): The velocity at the end of the node.
    """
    try:
        traction_limit = model.traction_limited_acceleration(
            ctx, initial_velocity
        )
        power_limit = model.power_limited_acceleration(ctx, initial_velocity)
        acceleration = min(traction_limit, power_limit)

        final_velocity = math.sqrt(
            initial_velocity**2 + 2 * acceleration * ctx.node.length
        )
    except ValueError:  # TODO
        final_velocity = initial_velocity

    return final_velocity
