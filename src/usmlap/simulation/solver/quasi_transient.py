"""
This module implements a quasi-transient solver.
"""

import logging
from dataclasses import dataclass

from rich.progress import Progress

from usmlap.model.errors import OutOfChargeError

from ..solution import Solution
from .quasi_steady_state import QuasiSteadyStateSolver
from .solver_interface import (
    MaximumIterationsExceededError,
    SolverError,
    SolverInterface,
)
from .transient_variable import update_transient_variables

MAXIMUM_TRANSIENT_ITERATIONS = 100
CONVERGENCE_TOLERANCE = 1e-4
TASK_DESCRIPTION = "Solving transient simulation..."


@dataclass
class BelowTargetSOCError(SolverError):
    """Error raised when the finishing SOC is below the target SOC."""

    final_soc: float
    target_soc: float

    def __str__(self) -> str:
        return f"Final SOC of {self.final_soc:.3f} is below the target SOC of {self.target_soc:.3f}."

    def overshoot(self, initial_soc: float) -> float:
        return (initial_soc - self.final_soc) / (initial_soc - self.target_soc)


class QuasiTransientSolver(SolverInterface):
    """
    Quasi-transient solver.
    """

    target_soc: float = 0.2

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

                while True:
                    try:
                        solution = self._solve_next_iteration(solution)
                        solution = self._recalculate_state_variables(solution)
                        break
                    except OutOfChargeError:
                        self._decrease_discharge_limit(0.9)

                    except BelowTargetSOCError as e:
                        initial_soc = 1  # TODO
                        scaling_factor = e.overshoot(initial_soc) * 1.01
                        self._decrease_discharge_limit(1 / scaling_factor)

                times.append(solution.total_time)
                logging.info(f"Iteration {i}, time: {solution.total_time:.3f}s")

                if _convergence_achieved(times, CONVERGENCE_TOLERANCE):
                    logging.info(f"Converged after {i} iterations.")
                    return solution

        raise MaximumIterationsExceededError(
            MAXIMUM_TRANSIENT_ITERATIONS, CONVERGENCE_TOLERANCE, times
        )

    def _decrease_discharge_limit(self, scaling_factor: float) -> None:
        powertrain = self.global_context.vehicle.powertrain
        old_limit = powertrain.discharge_current_limit
        new_limit = old_limit * scaling_factor
        powertrain.discharge_current_limit = new_limit
        logging.warning(
            f"Discharge current limit decreased from {old_limit} to {new_limit}"
        )

    def _solve_next_iteration(self, previous_solution: Solution) -> Solution:
        """
        Calculate the next iteration of the solution.

        This is done by calling the `QuasiSteadyStateSolver`.

        Args:
            previous_solution (Solution): The previous iteration of the solution.

        Returns:
            solution (Solution): The next iteration of the solution.
        """
        solver = QuasiSteadyStateSolver(self.vehicle_model, self.global_context)
        solution = solver.solve(previous_solution)

        return solution

    def _recalculate_state_variables(self, solution: Solution) -> Solution:
        """
        Recalculate the state variables of the vehicle.

        Args:
            solution (Solution): The solution object.

        Returns:
            solution (Solution): The solution with updated state variables.
        """
        for i in range(1, len(solution.nodes)):
            previous_node = solution.nodes[i - 1]
            ctx = self.local_context(
                previous_node.track_node, previous_node.transient_variables
            )
            solution.nodes[i].transient_variables = update_transient_variables(
                ctx=ctx,
                initial_state=previous_node.transient_variables,
                dt=previous_node.time,
                vehicle_state=previous_node.calculated_vehicle_state,  # noqa
            )

        final_soc = solution.nodes[-1].transient_variables.soc
        if final_soc < self.target_soc:
            raise BelowTargetSOCError(final_soc, self.target_soc)
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
