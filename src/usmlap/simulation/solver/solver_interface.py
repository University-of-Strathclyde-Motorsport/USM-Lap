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


class MaximumIterationsExceededError(SolverError):
    """
    Error raised when the maximum number of iterations is exceeded
    without converging on a solution.
    """

    pass


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
