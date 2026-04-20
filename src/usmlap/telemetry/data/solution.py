"""
This module defines a format for storing the solution of a simulation.
"""

from dataclasses import dataclass

from usmlap.simulation import Solution
from usmlap.simulation.solver import SolverInterface
from usmlap.vehicle import Vehicle


@dataclass(frozen=True)
class TelemetrySolution(object):
    """A solution object."""

    vehicle: Vehicle
    solution: Solution
    solver: type[SolverInterface]


def create_telemetry_solution(
    vehicle: Vehicle, solution: Solution
) -> TelemetrySolution:
    """Create a telemetry solution."""
    return TelemetrySolution(vehicle=vehicle, solution=solution)
