"""
This module implements a quasi-steady-state solver.
"""

import logging

from rich import progress
from scipy.signal import find_peaks

from ..solution import Solution
from ..vehicle_state import StateVariables
from .acceleration import calculate_next_velocity
from .apex_velocity import solve_apex_velocity
from .braking import calculate_initial_velocity
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
        solution = _solve_maximum_velocities(solution)

        logger.info("Finding apexes...")
        solution.set_apexes(_find_apexes(solution))

        logger.info("Solving forward propagation...")
        for apex in progress.track(
            solution.get_sorted_apex_indices(),
            description="Solving forward propagation...",
            transient=True,
        ):
            if solution.nodes[apex].is_apex():
                solution = _propagate_forward(solution, start_index=apex)

        logger.info("Solving backward propagation...")
        for apex in progress.track(
            solution.get_sorted_apex_indices(),
            description="Solving backward propagation...",
            transient=True,
        ):
            if solution.nodes[apex].is_apex():
                solution = _propagate_backward(solution, start_index=apex)

        logger.info("Resolving full vehicle state...")
        solution.evaluate_full_vehicle_state(solution.vehicle_model)

        logger.info("Recalculating state variables...")
        solution = _recalculate_state_variables(solution)

        return solution


def _solve_maximum_velocities(solution: Solution) -> Solution:
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
    previous_velocity = None
    for node in progress.track(
        solution.nodes,
        description="Solving maximum velocities...",
        transient=True,
    ):
        velocity = solve_apex_velocity(
            vehicle_model=solution.vehicle_model,
            state_variables=node.state_variables,
            node=node.track_node,
            velocity_estimate=previous_velocity,
        )
        node.maximum_velocity = velocity
        previous_velocity = velocity
    return solution


def _find_apexes(solution: Solution) -> list[int]:
    """
    Identify the apexes of a solution.

    Apexes are the indices at which the maximum velocity is a local minimum.

    Args:
        solution (Solution): The solution to analyse.

    Returns:
        apexes (list[int]): The indices of the apexes.
    """
    maximum_velocities = [-node.maximum_velocity for node in solution]
    apex_indices, _ = find_peaks(maximum_velocities)
    apex_indices = set(apex_indices.tolist())
    apex_indices.update([0, len(solution.nodes) - 1])
    return list(apex_indices)


def _propagate_forward(solution: Solution, start_index: int) -> Solution:
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
        potential_velocity = calculate_next_velocity(
            vehicle_model=solution.vehicle_model,
            state=node.state_variables,
            node=node.track_node,
            initial_velocity=node.initial_velocity,
        )

        final_velocity = min(potential_velocity, node.maximum_velocity)

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


def _propagate_backward(solution: Solution, start_index: int) -> Solution:
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

        potential_velocity = calculate_initial_velocity(
            vehicle_model=solution.vehicle_model,
            state=node.state_variables,
            node=node.track_node,
            final_velocity=node.final_velocity,
        )

        initial_velocity = min(potential_velocity, node.previous.final_velocity)

        node.set_initial_velocity(initial_velocity)
        node.previous.set_final_velocity(initial_velocity)

    logger.debug(f"Solved backward propogation of apex {start_index}.")
    return solution


def _recalculate_state_variables(solution: Solution) -> Solution:
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
