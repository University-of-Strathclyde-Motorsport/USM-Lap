"""
This module defines the interface for simulation solvers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from usmlap.simulation import Environment, LambdaCoefficients
from usmlap.simulation.model import VehicleModelInterface
from usmlap.simulation.model.context import Context
from usmlap.simulation.vehicle_state import StateVariables
from usmlap.track import TrackNode
from usmlap.vehicle import Vehicle

from ..solution import Solution


class SolverError(Exception):
    """Base class for simulation solver errors."""

    pass


class MaximumIterationsExceededError(SolverError):
    """
    Error raised when the maximum number of iterations is exceeded
    without converging on a solution.
    """

    pass


@dataclass
class SolverInterface(ABC):
    """
    Abstract base class for simulation solvers.
    """

    vehicle_model: VehicleModelInterface
    vehicle: Vehicle
    environment: Environment
    lambdas: LambdaCoefficients

    @abstractmethod
    def solve(self, previous_solution: Solution) -> Solution: ...

    def get_context(self, node: TrackNode, state: StateVariables) -> Context:
        return Context(
            environment=self.environment,
            vehicle=self.vehicle,
            state=state,
            node=node,
            lambdas=self.lambdas,
        )
