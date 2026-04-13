"""
This module implements the braking solver,
which calculates the maximum possible braking at a node.
"""

import math

from usmlap.model import Context, VehicleModelInterface


def calculate_initial_velocity(
    vehicle_model: VehicleModelInterface, ctx: Context, final_velocity: float
) -> float:
    """
    Calculate the velocity at the start of a node,
    given the final velocity at the end of the node.

    Args:
        vehicle_model (VehicleModelInterface): The vehicle model to use.
        state (StateVariables): The vehicle's state variables.
        node (TrackNode): The track node to solve.
        final_velocity (float): The velocity at the end of the node.

    Returns:
        initial_velocity (float): The velocity at the start of the node.
    """

    try:
        deceleration = vehicle_model.traction_limited_braking(
            ctx, final_velocity
        )

        initial_velocity = math.sqrt(
            final_velocity**2 + 2 * deceleration * ctx.node.length
        )

    except ValueError:
        initial_velocity = final_velocity

    return initial_velocity
