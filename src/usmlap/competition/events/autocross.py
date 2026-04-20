"""
This module defines the autocross event at Formula Student.
"""

from dataclasses import InitVar, dataclass, field

from usmlap.simulation import SimulationSettings, simulate
from usmlap.solver import Solution
from usmlap.track import Mesh, TrackData, generate_mesh
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

    track_file: InitVar[str]
    track_data: TrackData = field(init=False)

    def __post_init__(self, track_file: str) -> None:
        self.track_data = TrackData.from_json(track_file)

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
        return generate_mesh(self.track_data, resolution)
