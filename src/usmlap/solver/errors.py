"""
This module defines custom error types for simulation solvers.
"""

from dataclasses import dataclass


class SolverError(Exception):
    """Base class for solver errors."""

    pass


@dataclass
class AlgorithmError(SolverError):
    """
    Error raised when the solver algorithm behaves unexpectedly.
    This indicates that there is a bug in the code.
    """

    message: str

    def __str__(self) -> str:
        return f"Algorithm error: {self.message}"


@dataclass
class MaximumIterationsExceededError(SolverError):
    """
    Error raised when the maximum number of iterations is exceeded
    without converging on a solution.
    """

    iterations: int
    precision: float
    residuals: list[float]

    @property
    def _final_error(self) -> float:
        if len(self.residuals) < 2:
            return 0
        return abs(self.residuals[-1] - self.residuals[-2])

    def __str__(self) -> str:
        return (
            f"Failed to converge to desired precision {self.precision} "
            f"after {self.iterations} iterations. "
            f"Final error: {self._final_error}\n"
            f"Residuals: {self.residuals}"
        )


@dataclass
class BelowTargetSOCError(SolverError):
    """Error raised when the finishing SOC is below the target SOC."""

    final_soc: float
    target_soc: float

    def __str__(self) -> str:
        return f"Final SOC of {self.final_soc:.3f} is below the target SOC of {self.target_soc:.3f}."

    def overshoot(self, initial_soc: float) -> float:
        return (initial_soc - self.final_soc) / (initial_soc - self.target_soc)
