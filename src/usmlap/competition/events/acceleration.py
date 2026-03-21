"""
This module defines the acceleration event at Formula Student.
"""

from dataclasses import dataclass

from usmlap.simulation import SimulationSettings, Solution, simulate
from usmlap.track import Mesh, MeshGenerator, load_track_from_spreadsheet
from usmlap.vehicle import Vehicle

from ..points import (
    ACCELERATION_COEFFICIENTS,
    CompetitionData,
    CompetitionPoints,
    calculate_points,
)
from .event import EventInterface

ACCELERATION_TRACK = "Acceleration.xlsx"


@dataclass
class Acceleration(EventInterface, label="acceleration"):
    """
    Acceleration event at Formula Student.
    """

    track_data = load_track_from_spreadsheet(ACCELERATION_TRACK)

    def simulate_event(
        self, vehicle: Vehicle, settings: SimulationSettings
    ) -> Solution:
        mesh = self.get_mesh(settings.mesh_resolution)
        solution = simulate(vehicle, mesh, settings)
        return solution

    def calculate_points(
        self, solution: Solution, data: CompetitionData
    ) -> CompetitionPoints:
        t_team = solution.total_time
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
        return MeshGenerator(resolution).generate_mesh(self.track_data)
