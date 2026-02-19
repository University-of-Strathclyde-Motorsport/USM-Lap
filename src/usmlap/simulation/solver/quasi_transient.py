"""
This module implements a quasi-transient solver.
"""

import logging

from usmlap.simulation.solution import Solution

from .quasi_steady_state import QuasiSteadyStateSolver
from .solver_interface import SolverInterface

MAXIMUM_TRANSIENT_ITERATIONS = 100
CONVERGENCE_TOLERANCE = 1e-4


class QuasiTransientSolver(SolverInterface):
    """
    Quasi-transient solver.
    """

    @staticmethod
    def solve(previous_solution: Solution) -> Solution:
        times: list[float] = []
        solution = previous_solution

        for i in range(MAXIMUM_TRANSIENT_ITERATIONS):
            solution = _solve_next_iteration(previous_solution=solution)
            times.append(solution.total_time)
            logging.info(f"Iteration {i}, time: {solution.total_time:.3f}s")

            if _convergence_achieved(times, CONVERGENCE_TOLERANCE):
                logging.info(f"Converged after {i} iterations.")
                break

        return solution


def _solve_next_iteration(previous_solution: Solution) -> Solution:
    """
    Calculate the next iteration of the solution.

    This is done by calling the `QuasiSteadyStateSolver`.

    Args:
        previous_solution (Solution): The previous iteration of the solution.

    Returns:
        solution (Solution): The next iteration of the solution.
    """
    solution = QuasiSteadyStateSolver().solve(previous_solution)
    return solution


def _convergence_achieved(times: list[float], threshold: float) -> bool:
    """
    Check if the solution has converged.

    This is done by checking if the difference in solution times
    between the previous two iterations
    is below a certain threshold.

    Args:
        times (list[float]): The total times for each iteration.
        threshold (float): The threshold for convergence.

    Returns:
        converged (bool):
            `True` if the solution has converged, otherwise `False`.
    """
    if len(times) < 2:
        return False

    converged = abs(times[-1] - times[-2]) < threshold
    return converged
