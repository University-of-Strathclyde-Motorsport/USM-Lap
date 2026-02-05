"""
This module implements a quasi-steady-state solver.
"""

import logging
from math import sqrt

from scipy.signal import find_peaks

from simulation.model.vehicle_model import VehicleModelInterface
from simulation.solution import Solution, SolutionNode, create_new_solution
from simulation.vehicle_state import StateVariables
from track.mesh import Mesh

from .solver_interface import SolverInterface

logger = logging.getLogger(__name__)


class QuasiSteadyStateSolver(SolverInterface):
    """
    Quasi-steady-state solver.
    """

    @staticmethod
    def solve(
        vehicle_model: VehicleModelInterface, track_mesh: Mesh
    ) -> Solution:
        logger.info("Creating new solution...")
        solution = create_new_solution(track_mesh, vehicle_model)
        solution.nodes[0].anchor_initial_velocity(0)

        logger.info("Solving maximum velocities...")
        solution = solve_maximum_velocities(solution)

        logger.info("Finding apexes...")
        solution.apexes = find_apexes(solution)

        logger.info("Solving forward propagation...")
        for apex in solution.apexes.copy():
            if apex in solution.apexes:
                solution = propagate_forward(solution, apex)

        logger.info("Solving backward propagation...")
        for apex in solution.apexes.copy():
            if apex in solution.apexes:
                solution = propagate_backward(solution, apex)

        logger.info("Resolving full vehicle state...")
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
    vehicle_model = solution.vehicle_model.lateral_vehicle_model
    for node in solution.nodes:
        node.maximum_velocity = vehicle_model(node.track_node).velocity
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
    maximum_velocities = [-node.maximum_velocity for node in solution.nodes]
    apex_indices, _ = find_peaks(maximum_velocities)
    apex_indices = set(apex_indices.tolist())
    apex_indices.update([0, len(solution.nodes) - 1])
    apex_velocities = [solution.nodes[i].maximum_velocity for i in apex_indices]
    _, sorted_apexes = zip(*sorted(zip(apex_velocities, apex_indices)))
    apexes = list(sorted_apexes)
    logger.debug(f"Identified {len(apexes)} apexes: {apexes}")
    return apexes


def propagate_forward(solution: Solution, apex: int) -> Solution:
    """
    Propagate the solution forward.

    Args:
        solution (Solution): The initial solution.

    Returns:
        solution (Solution): The forward-propagated solution.
    """

    logger.debug(f"Forward propagating apex {apex}")

    maximum_velocity = solution.nodes[apex].maximum_velocity
    solution.nodes[apex].set_initial_velocity(maximum_velocity)

    i = apex
    while i < len(solution.nodes):
        current_node = solution.nodes[i]

        maximum_velocity = current_node.maximum_velocity
        traction_limited_velocity = traction_limit_velocity(
            solution.vehicle_model, current_node
        )
        final_velocity = min(traction_limited_velocity, maximum_velocity)

        current_node.set_final_velocity(final_velocity)

        if i >= len(solution.nodes) - 1:
            break

        next_node = solution.nodes[i + 1]
        next_node.set_initial_velocity(final_velocity)

        if i + 1 in solution.apexes:
            if final_velocity < next_node.maximum_velocity:
                logger.debug(f"Removing apex {i + 1}")
                solution.apexes.remove(i + 1)
            else:
                break

        i += 1

    logger.debug(f"Solved forward propogation of apex {apex}.")
    return solution


def propagate_backward(solution: Solution, apex: int) -> Solution:
    """
    Propagate the solution backwards.

    Args:
        solution (Solution): The initial solution.

    Returns:
        solution (Solution): The backward-propagated solution.
    """

    logger.debug(f"Backward propagating apex {apex}")

    i = apex
    while i > 0:
        current_node = solution.nodes[i]
        previous_node = solution.nodes[i - 1]

        maximum_velocity = previous_node.final_velocity
        if maximum_velocity <= current_node.final_velocity:
            break

        traction_limit_velocity = traction_limit_velocity_braking(
            solution.vehicle_model, current_node
        )
        initial_velocity = min(traction_limit_velocity, maximum_velocity)

        current_node.set_initial_velocity(initial_velocity)
        previous_node.set_final_velocity(initial_velocity)

        if i - 1 in solution.apexes:
            if initial_velocity < previous_node.final_velocity:
                logger.debug(f"Removing apex {i + 1}")
                solution.apexes.remove(i - 1)
            else:
                break

        i -= 1

    logger.debug(f"Solved backward propogation of apex {apex}.")
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
        state_variables = StateVariables(
            velocity=node_solution.initial_velocity
        )
        traction_limited_acceleration = vehicle_model.calculate_acceleration(
            node=node_solution.track_node, state_variables=state_variables
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
        state_variables = StateVariables(velocity=node_solution.final_velocity)
        traction_limited_decceleration = vehicle_model.calculate_decceleration(
            node=node_solution.track_node, state_variables=state_variables
        )
        traction_limited_velocity = calculate_previous_velocity(
            final_velocity=node_solution.final_velocity,
            decceleration=traction_limited_decceleration,
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
    final_velocity: float, decceleration: float, displacement: float
) -> float:
    term = final_velocity**2 + 2 * decceleration * displacement
    if term <= 0:
        return 0
    else:
        return sqrt(term)
