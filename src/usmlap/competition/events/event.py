"""
This module defines the interface for Formula Student events.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import ClassVar

from usmlap.simulation.simulation import SimulationSettings, simulate
from usmlap.simulation.solution import Solution
from usmlap.track.mesh import Mesh, MeshGenerator
from usmlap.track.track_data import TrackData
from usmlap.vehicle.vehicle import Vehicle

from ..settings import CompetitionSettings


@dataclass
class EventInterface(ABC):
    """
    Interface for Formula Student events.

    Attributes:
        label (str): Name of the event.
        simulation_settings (SimulationSettings):
            Settings for the simulation.
        competition_settings (CompetitionSettings):
            Settings for the competition.
        track_data (TrackData):
            Track data for the event.
        track_mesh (Mesh):
            Track mesh for the event.
    """

    name: ClassVar[str]
    simulation_settings: SimulationSettings
    competition_settings: CompetitionSettings
    track_data: TrackData = field(init=False)
    track_mesh: Mesh = field(init=False)

    def __init_subclass__(cls: type[EventInterface], label: str) -> None:
        super().__init_subclass__()
        cls.label = label

    def __post_init__(self) -> None:
        self.track_data = self.load_track()
        self.track_mesh = self.generate_mesh()

    @abstractmethod
    def load_track(self) -> TrackData: ...

    def generate_mesh(self) -> Mesh:
        track_data = self.load_track()
        return MeshGenerator(resolution=1).generate_mesh(track_data)

    def get_simulation_settings(self) -> SimulationSettings:
        return self.simulation_settings

    def modify_vehicle_for_event(self, vehicle: Vehicle) -> Vehicle:
        return vehicle

    def simulate(self, vehicle: Vehicle) -> Solution:
        vehicle = self.modify_vehicle_for_event(vehicle)
        solution = simulate(
            vehicle=vehicle,
            track_mesh=self.track_mesh,
            settings=self.get_simulation_settings(),
        )
        return solution
