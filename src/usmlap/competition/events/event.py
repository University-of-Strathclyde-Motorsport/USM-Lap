"""
This module defines the interface for Formula Student events."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import NamedTuple

from usmlap.competition.points import CompetitionData, CompetitionPoints
from usmlap.simulation.settings import SimulationSettings
from usmlap.telemetry.data.solution import TelemetrySolution
from usmlap.track.mesh import Mesh
from usmlap.vehicle.vehicle import Vehicle


class EventTuple[T](NamedTuple):
    acceleration: T | None = None
    skidpad: T | None = None
    autocross: T | None = None
    endurance: T | None = None
    efficiency: T | None = None


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
        self,
        vehicle: Vehicle,
        settings: SimulationSettings,
    ) -> TelemetrySolution: ...

    @abstractmethod
    def calculate_points(
        self,
        solution: TelemetrySolution,
        data: CompetitionData,
    ) -> CompetitionPoints: ...
