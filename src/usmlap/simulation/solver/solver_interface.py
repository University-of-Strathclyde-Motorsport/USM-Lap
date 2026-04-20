"""
This module defines the interface for simulation solvers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from usmlap.model import (
    GlobalContext,
    NodeContext,
    StateVariables,
    VehicleModelInterface,
)
from usmlap.track import TrackNode

from ..solution import Solution


class SolverError(Exception):
    """Base class for simulation solver errors."""

    pass


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
class SolverInterface(ABC):
    """
    Abstract base class for simulation solvers.
    """

    vehicle_model: VehicleModelInterface
    global_context: GlobalContext

    @abstractmethod
    def solve(self, previous_solution: Solution) -> Solution: ...

    def local_context(
        self, node: TrackNode, state: StateVariables
    ) -> NodeContext:
        return self.global_context.get_local_context(node, state)
