"""
This module defines the interface for simulation solvers.
"""

from abc import ABC, abstractmethod
from simulation.solution import Solution
from simulation.model.vehicle_model import VehicleModelInterface
from track.mesh import Mesh


class SolverInterface(ABC):
    """
    Abstract base class for simulation solvers.
    """

    vehicle_model: VehicleModelInterface
    track_mesh: Mesh
    solution: Solution = Solution()

    def __init__(
        self, vehicle_model: VehicleModelInterface, track_mesh: Mesh
    ) -> None:
        self.vehicle_model = vehicle_model
        self.track_mesh = track_mesh

    @abstractmethod
    def solve(self) -> Solution: ...
