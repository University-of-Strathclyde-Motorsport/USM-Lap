"""
This module defines the interface for simulation solvers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from usmlap.model import (
    GlobalContext,
    NodeContext,
    TransientVariables,
    VehicleModelInterface,
)
from usmlap.track import TrackNode

from .solution import Solution


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
        self, node: TrackNode, state: TransientVariables
    ) -> NodeContext:
        return self.global_context.get_local_context(node, state)
