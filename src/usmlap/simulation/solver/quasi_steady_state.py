"""
This module implements a quasi-steady-state solver.
"""

import logging
from math import sqrt

from rich import progress
from scipy.signal import find_peaks

from usmlap.simulation.model.vehicle_model import VehicleModelInterface
from usmlap.simulation.solution import Solution, SolutionNode
from usmlap.simulation.vehicle_state import StateVariables

from .solver_interface import SolverInterface

logger = logging.getLogger(__name__)


class QuasiSteadyStateSolver(SolverInterface):
    """
    Quasi-steady-state solver.
    """

    @staticmethod
    def solve(previous_solution: Solution) -> Solution:

        solution = previous_solution

        solution.nodes[0].anchor_initial_velocity(0)

        logger.info("Solving maximum velocities...")
        solution = solve_maximum_velocities(solution)

        logger.info("Finding apexes...")
        solution.set_apexes(find_apexes(solution))

        logger.info("Solving forward propagation...")
        for apex in progress.track(
            solution.get_sorted_apex_indices(),
            description="Solving forward propagation...",
        ):
            if solution.nodes[apex].is_apex():
                solution = propagate_forward(solution, start_index=apex)

        logger.info("Solving backward propagation...")
        for apex in progress.track(
            solution.get_sorted_apex_indices(),
            description="Solving backward propagation...",
        ):
            if solution.nodes[apex].is_apex():
                solution = propagate_backward(solution, start_index=apex)

        logger.info("Resolving full vehicle state...")
        solution.evaluate_full_vehicle_state(solution.vehicle_model)

        logger.info("Recalculating state variables...")
        solution = recalculate_state_variables(solution)

        return solution


def solve_maximum_velocities(solution: Solution) -> Solution:
    """
    Calculate the theoretical maximum velocity at each node.

    Nodes are solved independently of each other.
    Only the potential lateral acceleration of the vehicle is considered.
    The potential longitudinal acceleration is assumed to be infinite.

    Args:
        solution (Solution): The solution with no maximum velocities.

    Returns:
        solution (Solution): The solution with maximum velocities solved.
    """
    lateral_vehicle_model = solution.vehicle_model.lateral_vehicle_model
    for node in progress.track(
        solution, description="Solving maximum velocities..."
    ):
        node.maximum_velocity = lateral_vehicle_model(
            node.state_variables, node.track_node
        )
    return solution


def find_apexes(solution: Solution) -> list[int]:
    """
    Identify the apexes of a solution.

    Apexes are the indices at which the maximum velocity is a local minimum.

    Args:
        solution (Solution): The solution to analyze.

    Returns:
        apexes (list[int]): The indices of the apexes.
    """
    maximum_velocities = [-node.maximum_velocity for node in solution]
    apex_indices, _ = find_peaks(maximum_velocities)
    apex_indices = set(apex_indices.tolist())
    apex_indices.update([0, len(solution.nodes) - 1])
    return list(apex_indices)


def propagate_forward(solution: Solution, start_index: int) -> Solution:
    """
    Propagate the solution forward.

    Args:
        solution (Solution): The initial unpropagated solution.
        start_index (int): The index of the node to begin propagating from.

    Returns:
        solution (Solution): The forward-propagated solution.
    """
    logger.debug(f"Forward propagating from apex {start_index}")

    maximum_velocity = solution.nodes[start_index].maximum_velocity
    solution.nodes[start_index].set_initial_velocity(maximum_velocity)

    for node in solution.nodes[start_index:]:
        traction_limited_velocity = traction_limit_velocity(
            solution.vehicle_model, node
        )
        final_velocity = min(traction_limited_velocity, node.maximum_velocity)

        node.set_final_velocity(final_velocity)
        if node.next is None:
            break
        node.next.set_initial_velocity(final_velocity)

        if node.next.is_apex():
            if final_velocity < node.next.maximum_velocity:
                node.next.remove_apex()
            else:
                break

    logger.debug(f"Solved forward propogation of apex {start_index}.")
    return solution


def propagate_backward(solution: Solution, start_index: int) -> Solution:
    """
    Propagate the solution backwards.

    Args:
        solution (Solution): The initial unpropagated solution.
        start_index (int): The index of the node to begin propagating from.

    Returns:
        solution (Solution): The backward-propagated solution.
    """

    logger.debug(f"Backward propagating apex {start_index}")

    for node in solution.nodes[start_index::-1]:
        if node.previous is None:
            break

        if node.previous.final_velocity < node.final_velocity:
            break

        if node.previous.is_apex():
            node.previous.remove_apex()

        traction_limit_velocity = traction_limit_velocity_braking(
            solution.vehicle_model, node
        )
        initial_velocity = min(
            traction_limit_velocity, node.previous.final_velocity
        )

        node.set_initial_velocity(initial_velocity)
        node.previous.set_final_velocity(initial_velocity)

    logger.debug(f"Solved backward propogation of apex {start_index}.")
    return solution


def traction_limit_velocity(
    vehicle_model: VehicleModelInterface, node_solution: SolutionNode
) -> float:
    """
    Calculate the traction limited velocity at a node when accelerating.

    Args:
        vehicle_model (VehicleModelInterface): The vehicle model.
        node_solution (SolutionNode): The node solution.

    Returns:
        traction_limited_velocity (float): The traction limited velocity.
    """
    try:
        traction_limited_acceleration = vehicle_model.calculate_acceleration(
            node=node_solution.track_node,
            state_variables=node_solution.state_variables,
            velocity=node_solution.initial_velocity,
        )
        traction_limited_velocity = calculate_next_velocity(
            initial_velocity=node_solution.initial_velocity,
            acceleration=traction_limited_acceleration,
            displacement=node_solution.track_node.length,
        )
        return traction_limited_velocity
    except ValueError:
        return node_solution.initial_velocity  # TODO


def traction_limit_velocity_braking(
    vehicle_model: VehicleModelInterface, node_solution: SolutionNode
) -> float:
    """
    Calculate the traction limited velocity at a node when braking.

    Args:
        vehicle_model (VehicleModelInterface): The vehicle model.
        node_solution (SolutionNode): The node solution.

    Returns:
        traction_limited_velocity (float): The traction limited velocity.
    """
    try:
        traction_limited_deceleration = vehicle_model.calculate_deceleration(
            node=node_solution.track_node,
            state_variables=node_solution.state_variables,
            velocity=node_solution.final_velocity,
        )
        traction_limited_velocity = calculate_previous_velocity(
            final_velocity=node_solution.final_velocity,
            deceleration=traction_limited_deceleration,
            displacement=node_solution.track_node.length,
        )
        return traction_limited_velocity
    except ValueError:
        return node_solution.final_velocity  # TODO


def calculate_next_velocity(
    initial_velocity: float, acceleration: float, displacement: float
) -> float:
    return sqrt(initial_velocity**2 + 2 * acceleration * displacement)


def calculate_previous_velocity(
    final_velocity: float, deceleration: float, displacement: float
) -> float:
    term = final_velocity**2 + 2 * deceleration * displacement
    if term <= 0:
        return 0
    else:
        return sqrt(term)


def recalculate_state_variables(solution: Solution) -> Solution:
    """
    Recalculate the state variables of the vehicle.

    Args:
        solution (Solution): The solution object.

    Returns:
        solution (Solution): The solution with updated state variables.
    """
    for i in range(1, len(solution.nodes)):
        previous_node = solution.nodes[i - 1]
        updated_soc = (
            solution.vehicle_model.vehicle.powertrain.update_state_of_charge(
                state_of_charge=previous_node.state_variables.state_of_charge,
                energy_used=previous_node.energy_used,
            )
        )
        new_state_variables = StateVariables(state_of_charge=updated_soc)
        solution.nodes[i].state_variables = new_state_variables

    return solution
