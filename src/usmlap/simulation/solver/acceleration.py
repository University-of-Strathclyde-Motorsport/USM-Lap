"""
This module implements the acceleration solver,
which calculates the maximum possible acceleration at a node.
"""

import math

from usmlap.model import NodeContext, VehicleModelInterface
from usmlap.model.errors import InsufficientTractionError, WheelLiftError

MAXIMUM_ITERATIONS = 100
PRECISION = 1e-3


def calculate_next_velocity(
    model: VehicleModelInterface, ctx: NodeContext, initial_velocity: float
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
    axs: list[float] = [0]
    ay = ctx.node.curvature * initial_velocity**2

    resistive_fx = sum(model.resistive_forces(ctx, initial_velocity))
    drive_force = model.powertrain.drive_force(ctx, initial_velocity)

    for _ in range(1, MAXIMUM_ITERATIONS + 1):
        try:
            traction_force = model.longitudinal_traction(
                ctx, initial_velocity, axs[-1], ay=ay
            )
        except InsufficientTractionError as e:
            axs.append(axs[-1] / e.ratio)
            continue
        except WheelLiftError as e:
            scale_factor = (
                1 - (2 * e.max_wheel_lift) / e.longitudinal_load_transfer
            )
            axs.append(axs[-1] * scale_factor)
            continue

        limiting_force = min(traction_force, drive_force)
        net_force = limiting_force - resistive_fx

        ax = net_force / ctx.vehicle.equivalent_mass
        axs.append(ax)

        if abs(axs[-1] - axs[-2]) < PRECISION:
            break

    final_velocity = math.sqrt(
        initial_velocity**2 + 2 * axs[-1] * ctx.node.length
    )
    return final_velocity
