"""
This module defines the interface for simulation solvers.
"""

from abc import ABC, abstractmethod

from simulation.model.vehicle_model import VehicleModelInterface
from simulation.solution import Solution
from track.mesh import Mesh


class SolverInterface(ABC):
    """
    Abstract base class for simulation solvers.
    """

    @staticmethod
    @abstractmethod
    def solve(
        vehicle_model: VehicleModelInterface, track_mesh: Mesh
    ) -> Solution: ...
