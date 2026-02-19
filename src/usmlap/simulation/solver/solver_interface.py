"""
This module defines the interface for simulation solvers.
"""

from abc import ABC, abstractmethod

from usmlap.simulation.solution import Solution


class SolverInterface(ABC):
    """
    Abstract base class for simulation solvers.
    """

    @staticmethod
    @abstractmethod
    def solve(previous_solution: Solution) -> Solution: ...
