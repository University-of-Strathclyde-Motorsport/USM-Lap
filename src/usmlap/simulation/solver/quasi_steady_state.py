"""
This module implements a quasi-steady-state solver.
"""

import math
import logging

from scipy.signal import find_peaks

from simulation.model.vehicle_model import VehicleState
from .solver_interface import SolverInterface
from track.mesh import Mesh
from simulation.solution import Solution
from simulation.solution import Node as SolutionNode
from simulation.model.vehicle_model import VehicleModelInterface


class QuasiSteadyStateSolver(SolverInterface):
    """
    Quasi-steady-state solver.
    """

    @staticmethod
    def solve(
        vehicle_model: VehicleModelInterface, track_mesh: Mesh
    ) -> Solution:
        logging.info("Solving maximum velocities...")
        solution = solve_maximum_velocities(vehicle_model, track_mesh)
        solution.apexes = find_apexes(solution)
        solution.nodes[0].initial_velocity = 0

        logging.info("Solving forward propagation...")
        for apex in solution.apexes:
            solution = propagate_forward(solution, apex)

        logging.info("Solving backward propagation...")
        for apex in solution.apexes:
            solution = propagate_backward(solution, apex)

        return solution


def solve_maximum_velocities(
    vehicle_model: VehicleModelInterface, track_mesh: Mesh
) -> Solution:
    """
    Solve the maximum velocities of a track mesh.

    Args:
        vehicle_model (VehicleModelInterface): The vehicle model.
        track_mesh (Mesh): The track mesh.

    Returns:
        solution (Solution): The solution with maximum velocities solved.
    """
    solution_nodes: list[SolutionNode] = []
    for node in track_mesh.nodes:
        pure_lateral = vehicle_model.lateral_vehicle_model(node)
        node_solution = SolutionNode(
            track_node=node, maximum_velocity=pure_lateral.velocity
        )
        solution_nodes.append(node_solution)
    solution_nodes[0].maximum_velocity = 0
    return Solution(nodes=solution_nodes, vehicle_model=vehicle_model)


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
    return apexes


def propagate_forward(solution: Solution, apex: int) -> Solution:
    """
    Propagate the solution forward.

    Args:
        solution (Solution): The initial solution.

    Returns:
        solution (Solution): The forward-propagated solution.
    """
    if apex != 0:
        maximum_velocity = solution.nodes[apex].maximum_velocity
        solution.nodes[apex].initial_velocity = maximum_velocity

    i = apex
    while i < len(solution.nodes):
        current_node = solution.nodes[i]

        maximum_velocity = current_node.maximum_velocity
        traction_limited_velocity = traction_limit_velocity(
            solution.vehicle_model, current_node
        )
        final_velocity = min(traction_limited_velocity, maximum_velocity)

        current_node.final_velocity = final_velocity

        if i >= len(solution.nodes) - 1:
            break

        next_node = solution.nodes[i + 1]
        next_node.initial_velocity = final_velocity

        if i + 1 in solution.apexes:
            if final_velocity < next_node.maximum_velocity:
                solution.apexes.remove(i + 1)
            else:
                break

        i += 1

    return solution


def propagate_backward(solution: Solution, apex: int) -> Solution:
    """
    Propagate the solution backwards.

    Args:
        solution (Solution): The initial solution.

    Returns:
        solution (Solution): The backward-propagated solution.
    """
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

        current_node.initial_velocity = initial_velocity
        previous_node.final_velocity = initial_velocity

        if i - 1 in solution.apexes:
            if initial_velocity < previous_node.final_velocity:
                solution.apexes.remove(i - 1)
            else:
                break

        i -= 1
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
        vehicle_state = VehicleState(velocity=node_solution.initial_velocity)
        traction_limited_acceleration = vehicle_model.calculate_acceleration(
            node=node_solution.track_node,
            vehicle_state=vehicle_state,
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
        vehicle_state = VehicleState(velocity=node_solution.final_velocity)
        traction_limited_decceleration = vehicle_model.calculate_decceleration(
            node=node_solution.track_node, vehicle_state=vehicle_state
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
    return math.sqrt(initial_velocity**2 + 2 * acceleration * displacement)


def calculate_previous_velocity(
    final_velocity: float, decceleration: float, displacement: float
) -> float:
    term = final_velocity**2 + 2 * decceleration * displacement
    if term <= 0:
        return 0
    else:
        return math.sqrt(term)
