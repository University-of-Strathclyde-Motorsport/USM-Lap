"""
This module implements the apex solver,
which calculates the theoretical maximum velocity at each node,
assuming zero longitudinal acceleration.
"""

import math
from typing import Optional

from usmlap.track import TrackNode

from ..model import VehicleModelInterface
from ..vehicle_state import StateVariables
from .solver_interface import MaximumIterationsExceededError

PRECISION = 1e-2
MAXIMUM_ITERATIONS = 100


def solve_apex_velocity(
    vehicle_model: VehicleModelInterface,
    state_variables: StateVariables,
    node: TrackNode,
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
        vehicle_model (VehicleModelInterface):
            The vehicle model to use.
        state_variables (StateVariables):
            The vehicle's state variables.
        node (TrackNode):
            The track node to solve.
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

    maximum_velocity = vehicle_model.vehicle.maximum_velocity

    if node.curvature == 0:
        return maximum_velocity

    if velocity_estimate is None:
        velocity_estimate = maximum_velocity

    for i in range(1, maximum_iterations + 1):
        required_fy = abs(vehicle_model.required_fy(node, velocity_estimate))
        available_fy = vehicle_model.lateral_traction_limit(
            state_variables, node, velocity_estimate
        )
        fy_error = available_fy - required_fy
        # print(
        #     f"Iteration {i}, {velocity_estimate=}, {required_fy=:.1f}, {available_fy=:.1f}, {fy_error=}"
        # )
        if abs(fy_error) < precision:
            if fy_error > 0:
                return velocity_estimate
            else:
                fy_error -= precision

        velocity_estimate = _update_velocity_estimate(
            velocity=velocity_estimate,
            fy_error=fy_error,
            curvature=node.curvature,
            vehicle_mass=vehicle_model.vehicle.total_mass,
        )

        if velocity_estimate >= maximum_velocity:
            return maximum_velocity

    raise MaximumIterationsExceededError()


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
