"""
This module defines the interface for Formula Student events.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from usmlap.simulation.simulation import SimulationSettings, simulate
from usmlap.simulation.solution import Solution
from usmlap.track.mesh import Mesh, MeshGenerator
from usmlap.track.track_data import TrackData, load_track_from_spreadsheet
from usmlap.vehicle.vehicle import Vehicle

from ..points import CompetitionData


@dataclass
class EventInterface(ABC):
    """
    Interface for Formula Student events.

    Attributes:
        label (str): Name of the event.
        track_file (str): Path to the track file.
        track_data (TrackData): Track data for the event.
        track_mesh (Mesh): Track mesh for the event.
    """

    track_file: str
    track_data: TrackData = field(init=False)
    track_mesh: Mesh = field(init=False)

    def __init_subclass__(cls: type[EventInterface], label: str) -> None:
        super().__init_subclass__()
        cls.label = label

    def __post_init__(self) -> None:
        self.track_data = self.load_track(self.track_file)
        self.track_mesh = self.generate_mesh()

    def load_track(self, track_file: str) -> TrackData:
        track_data = load_track_from_spreadsheet(track_file)
        return track_data

    def generate_mesh(self) -> Mesh:
        return MeshGenerator(resolution=1).generate_mesh(self.track_data)

    def _modify_vehicle_for_event(self, vehicle: Vehicle) -> Vehicle:
        """
        Modify vehicle parameters for the event.
        Override this method if required.
        """
        return vehicle

    def _modify_simulation_settings_for_event(
        self, settings: SimulationSettings
    ) -> SimulationSettings:
        """
        Modify the simulation settings for the event.
        Override this method if required.
        """
        return settings

    def simulate(
        self, vehicle: Vehicle, settings: SimulationSettings
    ) -> Solution:
        """
        Simulate the event.

        Args:
            vehicle (Vehicle): The vehicle to simulate.
            settings (SimulationSettings): Settings for the simulation.

        Returns:
            solution (Solution): The solution to the event.
        """
        vehicle = self._modify_vehicle_for_event(vehicle)
        settings = self._modify_simulation_settings_for_event(settings)

        solution = simulate(
            vehicle=vehicle, track_mesh=self.track_mesh, settings=settings
        )
        return solution

    @abstractmethod
    def calculate_points(
        self, solution: Solution, competition_data: CompetitionData
    ) -> dict[str, float]: ...
