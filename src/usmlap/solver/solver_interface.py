"""
This module defines the interface for simulation solvers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import ClassVar

from usmlap.model import (
    GlobalContext,
    NodeContext,
    TractionModel,
    TransientVariables,
)
from usmlap.track import TrackNode

from .solution import Solution


@dataclass
class SolverInterface(ABC):
    """
    Abstract base class for simulation solvers.
    """

    _REGISTRY: ClassVar[dict[str, type[SolverInterface]]] = {}
    id: ClassVar[str]

    vehicle_model: TractionModel
    global_context: GlobalContext

    def __init_subclass__(cls: type[SolverInterface], id: str) -> None:
        super().__init_subclass__()  # noqa: S930
        cls._REGISTRY[id] = cls
        cls.id = id

    @abstractmethod
    def solve(self, previous_solution: Solution) -> Solution: ...

    def local_context(
        self,
        node: TrackNode,
        state: TransientVariables,
    ) -> NodeContext:
        return self.global_context.get_local_context(node, state)


def get_solver(solver: type[SolverInterface] | str) -> type[SolverInterface]:
    """Get a solver by id or name."""
    if not isinstance(solver, str):
        return solver
    if solver not in SolverInterface._REGISTRY:
        raise ValueError(f"Invalid solver id '{solver}'")
    return SolverInterface._REGISTRY[solver]
