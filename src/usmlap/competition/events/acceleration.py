"""
This module defines the acceleration event at Formula Student."""

from dataclasses import dataclass

from usmlap.competition.events.event import EventInterface
from usmlap.competition.points import (
    ACCELERATION_COEFFICIENTS,
    CompetitionData,
    CompetitionPoints,
    calculate_points,
)
from usmlap.simulation.settings import SimSettings
from usmlap.simulation.simulation import simulate
from usmlap.telemetry.data.solution import TelemetrySolution
from usmlap.track.mesh import Mesh
from usmlap.track.mesh_generation import generate_mesh
from usmlap.track.settings import TrackSettings
from usmlap.vehicle.vehicle import Vehicle

ACCELERATION_TRACK = r"data\tracks\FSAE Acceleration.json"


@dataclass
class Acceleration(EventInterface, label="acceleration"):
    """
    Acceleration event at Formula Student.
    """

    def simulate_event(
        self,
        vehicle: Vehicle,
        settings: SimSettings,
    ) -> TelemetrySolution:
        mesh = self.get_mesh(settings.track.resolution)
        solution = simulate(vehicle, mesh, settings)
        return solution

    def calculate_points(
        self,
        solution: TelemetrySolution,
        data: CompetitionData,
    ) -> CompetitionPoints:
        t_team = solution.solution.total_time
        t_min = data.acceleration_t_min
        points = calculate_points(t_team, t_min, ACCELERATION_COEFFICIENTS)[1]
        return {"acceleration": points}

    def _generate_mesh(self, resolution: float) -> Mesh:
        """
        Generate a track mesh for the acceleration event.

        Args:
            resolution (float): The resolution of the mesh.

        Returns:
            mesh (Mesh): A mesh of the track.

        """
        return generate_mesh(
            TrackSettings(track_file=ACCELERATION_TRACK, resolution=resolution)
        )
