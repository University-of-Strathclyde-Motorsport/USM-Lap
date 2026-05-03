"""
This module defines a format for storing the solution of a simulation.
"""

from __future__ import annotations

from dataclasses import dataclass

from usmlap.solver import Solution, SolutionNode, SolverInterface
from usmlap.vehicle import Vehicle


@dataclass(frozen=True)
class TelemetrySolution(object):
    """A solution object."""

    vehicle: Vehicle
    solution: Solution
    solver: type[SolverInterface]

    @property
    def nodes(self) -> list[SolutionNode]:
        return self.solution.nodes

    def get_subset(self, indices: list[int]) -> TelemetrySolution:
        return TelemetrySolution(
            vehicle=self.vehicle,
            solution=self.solution.get_subset(indices),
            solver=self.solver,
        )

    def get_sector_boundary_positions(self) -> list[float]:
        return self.solution.get_sector_boundary_positions()
