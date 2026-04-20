"""
This module implements a quasi-steady-state solver.
"""

import logging

from rich import progress
from scipy.signal import find_peaks

from usmlap.model.vehicle_state import VehicleMotion
from usmlap.solver.solution import Solution
from usmlap.solver.solver_interface import SolverInterface

from .acceleration import calculate_next_velocity
from .apex_velocity import solve_apex_velocity
from .braking import calculate_initial_velocity

logger = logging.getLogger(__name__)


class QuasiSteadyStateSolver(SolverInterface):
    """
    Quasi-steady-state solver.
    """

    def solve(self, previous_solution: Solution) -> Solution:

        solution = previous_solution

        solution.nodes[0].anchor_initial_velocity(0)

        logger.info("Solving maximum velocities...")
        solution = self._solve_maximum_velocities(solution)

        logger.info("Finding apexes...")
        solution.set_apexes(_find_apexes(solution))

        logger.info("Solving forward propagation...")
        for apex in progress.track(
            solution.get_sorted_apex_indices(),
            description="Solving forward propagation...",
            transient=True,
        ):
            if solution.nodes[apex].is_apex():
                solution = self._propagate_forward(solution, start_index=apex)

        logger.info("Solving backward propagation...")
        for apex in progress.track(
            solution.get_sorted_apex_indices(),
            description="Solving backward propagation...",
            transient=True,
        ):
            if solution.nodes[apex].is_apex():
                solution = self._propagate_backward(solution, start_index=apex)

        logger.info("Resolving full vehicle state...")
        for node in solution.nodes:
            ctx = self.local_context(node.track_node, node.transient_variables)
            motion = VehicleMotion(
                node.average_velocity,
                node.longitudinal_acceleration,
                node.lateral_acceleration,
            )
            node.calculated_vehicle_state = (
                self.vehicle_model.evaluate_full_vehicle_state(ctx, motion)
            )

        return solution

    def _solve_maximum_velocities(self, solution: Solution) -> Solution:
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
            ctx = self.local_context(node.track_node, node.transient_variables)
            velocity = solve_apex_velocity(
                vehicle_model=self.vehicle_model,
                ctx=ctx,
                velocity_estimate=previous_velocity,
            )
            node.maximum_velocity = velocity
            previous_velocity = velocity
        return solution

    def _propagate_forward(
        self, solution: Solution, start_index: int
    ) -> Solution:
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
            ctx = self.local_context(node.track_node, node.transient_variables)
            potential_velocity = calculate_next_velocity(
                model=solution.vehicle_model,
                ctx=ctx,
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

    def _propagate_backward(
        self, solution: Solution, start_index: int
    ) -> Solution:
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

            ctx = self.local_context(node.track_node, node.transient_variables)

            potential_velocity = calculate_initial_velocity(
                vehicle_model=solution.vehicle_model,
                ctx=ctx,
                final_velocity=node.final_velocity,
            )

            initial_velocity = min(
                potential_velocity, node.previous.final_velocity
            )

            node.set_initial_velocity(initial_velocity)
            node.previous.set_final_velocity(initial_velocity)

        logger.debug(f"Solved backward propogation of apex {start_index}.")
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
    maximum_velocities = [-node.apex_velocity for node in solution]
    apex_indices, _ = find_peaks(maximum_velocities)
    apex_indices = set(apex_indices.tolist())
    apex_indices.update([0, len(solution.nodes) - 1])
    return list(apex_indices)
