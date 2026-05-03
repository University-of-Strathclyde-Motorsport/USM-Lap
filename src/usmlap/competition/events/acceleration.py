"""
This module defines the acceleration event at Formula Student.
"""

from dataclasses import dataclass

from usmlap.simulation import SimulationSettings, simulate
from usmlap.telemetry import TelemetrySolution
from usmlap.track import Mesh, TrackData, generate_mesh
from usmlap.vehicle import Vehicle

from ..points import (
    ACCELERATION_COEFFICIENTS,
    CompetitionData,
    CompetitionPoints,
    calculate_points,
)
from .event import EventInterface

ACCELERATION_TRACK = "FSAE Acceleration"


@dataclass
class Acceleration(EventInterface, label="acceleration"):
    """
    Acceleration event at Formula Student.
    """

    track_data = TrackData.from_json(ACCELERATION_TRACK)

    def simulate_event(
        self, vehicle: Vehicle, settings: SimulationSettings
    ) -> TelemetrySolution:
        mesh = self.get_mesh(settings.mesh_resolution)
        solution = simulate(vehicle, mesh, settings)
        return solution

    def calculate_points(
        self, solution: TelemetrySolution, data: CompetitionData
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
        return generate_mesh(self.track_data, resolution)
