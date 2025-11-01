"""
This module defines the interface for simulation solvers.
"""

from abc import ABC, abstractmethod
from simulation.solution import Solution


class SolverInterface(ABC):
    """
    Abstract base class for simulation solvers.
    """

    @abstractmethod
    def solve(self) -> Solution: ...
