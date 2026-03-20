"""
This module defines the interface for Formula Student events.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from usmlap.simulation.simulation import SimulationSettings
from usmlap.simulation.solution import Solution
from usmlap.vehicle.vehicle import Vehicle

from ..points import CompetitionData, CompetitionPoints


class EventInterface(ABC):
    """
    Interface for Formula Student events.

    Attributes:
        label (str): Name of the event.
    """

    def __init_subclass__(cls: type[EventInterface], label: str) -> None:
        super().__init_subclass__()
        cls.label = label

    @abstractmethod
    def simulate_event(
        self, vehicle: Vehicle, settings: SimulationSettings
    ) -> Solution: ...

    @abstractmethod
    def calculate_points(
        self, solution: Solution, data: CompetitionData
    ) -> CompetitionPoints: ...
