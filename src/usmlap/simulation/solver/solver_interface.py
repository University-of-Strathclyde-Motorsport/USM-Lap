"""
This module defines the interface for simulation solvers.
"""

from abc import ABC, abstractmethod

from usmlap.simulation.solution import Solution


class SolverError(Exception):
    """Base class for simulation solver errors."""

    pass


class MaximumIterationsExceededError(SolverError):
    """
    Error raised when the maximum number of iterations is exceeded
    without converging on a solution.
    """

    pass


class SolverInterface(ABC):
    """
    Abstract base class for simulation solvers.
    """

    @staticmethod
    @abstractmethod
    def solve(previous_solution: Solution) -> Solution: ...
