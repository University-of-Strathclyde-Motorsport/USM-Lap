"""
This module defines the autocross event at Formula Student."""

from dataclasses import dataclass
from pathlib import Path

from usmlap.simulation.settings import SimulationSettings
from usmlap.simulation.simulation import simulate
from usmlap.telemetry import TelemetrySolution
from usmlap.track import Mesh, generate_mesh
from usmlap.track.settings import TrackSettings
from usmlap.vehicle import Vehicle

from ..points import (
    AUTOCROSS_COEFFICIENTS,
    CompetitionData,
    CompetitionPoints,
    calculate_points,
)
from .event import EventInterface


@dataclass
class Autocross(EventInterface, label="autocross"):
    """
    Autocross event at Formula Student.
    """

    track_file: Path

    def simulate_event(
        self,
        vehicle: Vehicle,
        settings: SimulationSettings,
    ) -> TelemetrySolution:
        mesh = self.get_mesh(settings.mesh_resolution)
        solution = simulate(vehicle, mesh, settings)
        return solution

    def calculate_points(
        self,
        solution: TelemetrySolution,
        data: CompetitionData,
    ) -> CompetitionPoints:
        t_team = solution.solution.total_time
        t_min = data.autocross_t_min
        points = calculate_points(t_team, t_min, AUTOCROSS_COEFFICIENTS)[1]
        return {"autocross": points}

    def _generate_mesh(self, resolution: float) -> Mesh:
        """
        Generate a track mesh for the autocross event.

        Args:
            resolution (float): The resolution of the mesh.

        Returns:
            mesh (Mesh): A mesh of the track.

        """
        return generate_mesh(
            TrackSettings(track_file=self.track_file, resolution=resolution)
        )
