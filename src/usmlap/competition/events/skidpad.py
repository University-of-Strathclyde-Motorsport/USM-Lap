"""
This module defines the skidpad event at Formula Student.
"""

from dataclasses import dataclass

from usmlap.simulation import SimulationSettings, simulate
from usmlap.solver import Solution
from usmlap.track import Mesh, TrackData, generate_mesh
from usmlap.vehicle import Vehicle

from ..points import (
    SKIDPAD_COEFFICIENTS,
    CompetitionData,
    CompetitionPoints,
    calculate_points,
)
from .event import EventInterface

SKIDPAD_TRACK = "FSAE Skidpad"
RIGHT_CIRCLE_TIMED_SECTOR = "Right Circle 2"
LEFT_CIRCLE_TIMED_SECTOR = "Left Circle 2"


@dataclass
class Skidpad(EventInterface, label="skidpad"):
    """
    Skidpad event at Formula Student.
    """

    track_data = TrackData.from_json(SKIDPAD_TRACK)

    def simulate_event(
        self, vehicle: Vehicle, settings: SimulationSettings
    ) -> Solution:
        mesh = self.get_mesh(settings.mesh_resolution)
        solution = simulate(vehicle, mesh, settings)
        return solution

    def event_time(self, solution: Solution) -> float:
        right_time = solution.get_sector_time(RIGHT_CIRCLE_TIMED_SECTOR)
        left_time = solution.get_sector_time(LEFT_CIRCLE_TIMED_SECTOR)
        return (right_time + left_time) / 2

    def calculate_points(
        self, solution: Solution, data: CompetitionData
    ) -> CompetitionPoints:
        t_team = self.event_time(solution)
        t_min = data.skidpad_t_min
        points = calculate_points(t_team, t_min, SKIDPAD_COEFFICIENTS)[1]
        return {"skidpad": points}

    def _generate_mesh(self, resolution: float) -> Mesh:
        """
        Generate a track mesh for the skidpad event.

        The track has 5 sectors:
            1. Runup
            2. Right circle lap 1 (untimed)
            3. Right circle lap 2 (timed)
            4. Left circle lap 1 (untimed)
            5. Left circle lap 2 (timed)

        Args:
            resolution (float): The resolution of the mesh.

        Returns:
            mesh (Mesh): A mesh of the skidpad track.
        """

        return generate_mesh(self.track_data, resolution, smooth=False)
