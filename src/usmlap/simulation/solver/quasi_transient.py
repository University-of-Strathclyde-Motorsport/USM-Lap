"""
This module implements a quasi-transient solver.
"""

import logging

from rich.progress import Progress

from ..solution import Solution
from .quasi_steady_state import QuasiSteadyStateSolver
from .solver_interface import MaximumIterationsExceededError, SolverInterface

MAXIMUM_TRANSIENT_ITERATIONS = 100
CONVERGENCE_TOLERANCE = 1e-4
TASK_DESCRIPTION = "Solving transient simulation..."


class QuasiTransientSolver(SolverInterface):
    """
    Quasi-transient solver.
    """

    def solve(self, previous_solution: Solution) -> Solution:
        times: list[float] = []
        solution = previous_solution

        with Progress(transient=True) as progress:
            task = progress.add_task(TASK_DESCRIPTION, total=None)
            for i in range(MAXIMUM_TRANSIENT_ITERATIONS):
                progress.update(
                    task,
                    advance=1,
                    description=f"{TASK_DESCRIPTION} ({i + 1}/?)",
                )

                solution = self._solve_next_iteration(solution)
                times.append(solution.total_time)
                logging.info(f"Iteration {i}, time: {solution.total_time:.3f}s")

                if _convergence_achieved(times, CONVERGENCE_TOLERANCE):
                    logging.info(f"Converged after {i} iterations.")
                    return solution

        raise MaximumIterationsExceededError()

    def _solve_next_iteration(self, previous_solution: Solution) -> Solution:
        """
        Calculate the next iteration of the solution.

        This is done by calling the `QuasiSteadyStateSolver`.

        Args:
            previous_solution (Solution): The previous iteration of the solution.

        Returns:
            solution (Solution): The next iteration of the solution.
        """
        solver = QuasiSteadyStateSolver(
            vehicle_model=self.vehicle_model,
            vehicle=self.vehicle,
            environment=self.environment,
            lambdas=self.lambdas,
        )
        solution = solver.solve(previous_solution)
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
