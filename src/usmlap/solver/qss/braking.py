"""
This module implements the braking solver,
which calculates the maximum possible braking at a node.
"""

import math

from usmlap.model import NodeContext, TractionModel
from usmlap.model.errors import InsufficientTractionError, WheelLiftError
from usmlap.model.vehicle_state import VehicleMotion

MAXIMUM_ITERATIONS = 100
PRECISION = 1e-3


def calculate_initial_velocity(
    vehicle_model: TractionModel, ctx: NodeContext, final_velocity: float
) -> float:
    """
    Calculate the velocity at the start of a node,
    given the final velocity at the end of the node.

    Args:
        vehicle_model (TractionModel): The vehicle model to use.
        state (TransientVariables): The vehicle's state variables.
        node (TrackNode): The track node to solve.
        final_velocity (float): The velocity at the end of the node.

    Returns:
        initial_velocity (float): The velocity at the start of the node.
    """
    axs: list[float] = [0]
    ay = ctx.node.curvature * final_velocity**2

    resistive_fx = sum(vehicle_model.resistive_forces(ctx, final_velocity))

    for _ in range(1, MAXIMUM_ITERATIONS + 1):
        try:
            motion = VehicleMotion(final_velocity, axs[-1], ay)
            traction = vehicle_model.braking_traction(ctx, motion)
        except InsufficientTractionError as e:
            axs.append(axs[-1] / e.ratio)
            continue
        except WheelLiftError as e:
            scale_factor = (
                1 - (2 * e.max_wheel_lift) / e.longitudinal_load_transfer
            )
            axs.append(axs[-1] * scale_factor)
            continue

        net_force = traction + resistive_fx
        ax = net_force / ctx.vehicle.equivalent_mass
        axs.append(ax)

        if abs(ax - axs[-2]) < PRECISION:
            break

    initial_velocity = math.sqrt(
        final_velocity**2 + 2 * axs[-1] * ctx.node.length
    )
    return initial_velocity
