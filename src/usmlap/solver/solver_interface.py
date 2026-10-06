"""
This module defines the interface for simulation solvers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from usmlap.model.context import (
    GlobalContext,
    NodeContext,
    TransientVariables,
)
from usmlap.model.traction.traction_model import TractionModel
from usmlap.solver.solution import Solution
from usmlap.track.mesh import TrackNode


@dataclass
class SolverInterface(ABC):
    """
    Abstract base class for simulation solvers.
    """

    vehicle_model: TractionModel
    global_context: GlobalContext

    @abstractmethod
    def solve(self, previous_solution: Solution) -> Solution: ...

    def local_context(
        self,
        node: TrackNode,
        state: TransientVariables,
    ) -> NodeContext:
        return self.global_context.get_local_context(node, state)
