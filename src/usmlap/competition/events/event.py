"""
This module defines the interface for Formula Student events.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import NamedTuple, Optional

from usmlap.simulation import SimulationSettings
from usmlap.solver import Solution
from usmlap.track import Mesh
from usmlap.vehicle import Vehicle

from ..points import CompetitionData, CompetitionPoints


class EventTuple[T](NamedTuple):
    acceleration: Optional[T] = None
    skidpad: Optional[T] = None
    autocross: Optional[T] = None
    endurance: Optional[T] = None
    efficiency: Optional[T] = None


class EventInterface(ABC):
    """
    Interface for Formula Student events.

    Attributes:
        label (str): Name of the event.
    """

    def __init_subclass__(cls: type[EventInterface], label: str) -> None:
        super().__init_subclass__()
        cls._meshes: dict[float, Mesh] = {}
        cls.label = label

    def get_mesh(self, resolution: float) -> Mesh:
        if resolution not in self._meshes:
            self._meshes[resolution] = self._generate_mesh(resolution)
        return self._meshes[resolution]

    @abstractmethod
    def _generate_mesh(self, resolution: float) -> Mesh: ...

    @abstractmethod
    def simulate_event(
        self, vehicle: Vehicle, settings: SimulationSettings
    ) -> Solution: ...

    @abstractmethod
    def calculate_points(
        self, solution: Solution, data: CompetitionData
    ) -> CompetitionPoints: ...
