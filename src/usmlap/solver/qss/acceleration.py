"""
This module implements the acceleration solver,
which calculates the maximum possible acceleration at a node.
"""

from usmlap.model import NodeContext, TractionModel
from usmlap.model.errors import InsufficientTractionError, WheelLiftError
from usmlap.model.vehicle_state import Trajectory

MAXIMUM_ITERATIONS = 100
PRECISION = 1e-3


def solve_acceleration(
    model: TractionModel, ctx: NodeContext, initial_velocity: float
) -> float:
    """
    Calculate the velocity at the end of a node,
    given the initial velocity at the start of the node.

    Args:
        vehicle_model (TractionModel): The vehicle model to use.
        state (TransientVariables): The vehicle's state variables.
        node (TrackNode): The track node to solve.
        initial_velocity (float): The velocity at the start of the node.

    Returns:
        final_velocity (float): The velocity at the end of the node.
    """
    initial_ax = 0
    trajectory = Trajectory(
        velocity=initial_velocity, ax=initial_ax, curvature=ctx.node.curvature
    )

    resistive_fx = sum(model.resistive_forces(ctx, initial_velocity))
    drive_force = model.powertrain.drive_force(ctx, initial_velocity)

    axs: list[float] = []

    for _ in range(1, MAXIMUM_ITERATIONS + 1):
        axs.append(trajectory.ax)
        try:
            traction_force = model.longitudinal_traction(ctx, trajectory)

        except InsufficientTractionError as e:
            trajectory.ax /= e.ratio
            continue

        except WheelLiftError as e:
            scale_factor = (
                1 - (2 * e.max_wheel_lift) / e.longitudinal_load_transfer
            )
            trajectory.ax *= scale_factor
            continue

        limiting_force = min(sum(traction_force), drive_force)
        net_force = limiting_force - resistive_fx
        trajectory.ax = net_force / ctx.vehicle.equivalent_mass

        if abs(trajectory.ax - axs[-1]) < PRECISION:
            break

    final_velocity = trajectory.next_velocity(ctx.node.length)
    return final_velocity
