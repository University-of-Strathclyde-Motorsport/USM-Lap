"""
This module defines a format for storing the solution of a simulation.
"""

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
