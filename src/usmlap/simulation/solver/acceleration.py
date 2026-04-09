"""
This module implements the acceleration solver,
which calculates the maximum possible acceleration at a node,
while generating sufficient lateral traction to follow the track.
"""

from usmlap.simulation.errors import InsufficientTractionError
from usmlap.simulation.model import VehicleModelInterface
from usmlap.simulation.vehicle_state import StateVariables
from usmlap.track import TrackNode

PRECISION = 1e-3
MAXIMUM_ITERATIONS = 100


def solve_acceleration(
    vehicle_model: VehicleModelInterface,
    state_variables: StateVariables,
    node: TrackNode,
    initial_velocity: float,
    precision: float = PRECISION,
    maximum_iterations: int = MAXIMUM_ITERATIONS,
):
    """
    Calculate the potential acceleration at a node.
    This is the maximum rate at which the vehicle can acceleration
    while maintaining lateral traction.

    Args:
        vehicle_model (VehicleModelInterface):
            The vehicle model to use.
        state_variables (StateVariables):
            The vehicle's state variables.
        node (TrackNode):
            The track node to solve.
        initial_velocity (float):
            The vehicle's velocity at the start of the node.
        precision (float):
            The maximum error allowed in the calculation.
        maximum_iterations (int):
            The maximum number of iterations to perform before raising an error.
            If high precision is required, this value may need to be increased.

    Returns:
        acceleration (float): Maximum possible acceleration of the vehicle.

    Raises:
        MaximumIterationsExceededError:
            If the maximum number of iterations is exceeded
            without converging on a solution.
    """

    # try:
    traction_limit = vehicle_model.traction_limited_acceleration(
        state_variables=state_variables, node=node, velocity=initial_velocity
    )
    # except InsufficientTractionError:
    #     print(
    #         f"Acceleration: insufficient traction ({initial_velocity=}, {node.curvature=})"
    #     )
    #     return initial_velocity  # TODO: this should never occur

    return traction_limit
