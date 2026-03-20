"""
This module defines the autocross event at Formula Student.
"""

from dataclasses import InitVar, dataclass, field

from usmlap.simulation.simulation import SimulationSettings, simulate
from usmlap.simulation.solution import Solution
from usmlap.track.mesh import Mesh, MeshGenerator
from usmlap.track.track_data import load_track_from_spreadsheet
from usmlap.vehicle.vehicle import Vehicle

from ..points import (
    AUTOCROSS_COEFFICIENTS,
    CompetitionData,
    CompetitionPoints,
    calculate_points,
)
from .event import EventInterface

DEFAULT_MESH_RESOLUTION = 1


@dataclass
class Autocross(EventInterface, label="autocross"):
    """
    Autocross event at Formula Student.
    """

    track_file: InitVar[str]
    mesh_resolution: float = DEFAULT_MESH_RESOLUTION
    track_mesh: Mesh = field(init=False)

    def __post_init__(self, track_file: str) -> None:
        track_data = load_track_from_spreadsheet(track_file)
        self.track_mesh = MeshGenerator(self.mesh_resolution).generate_mesh(
            track_data
        )

    def simulate_event(
        self, vehicle: Vehicle, settings: SimulationSettings
    ) -> Solution:
        solution = simulate(vehicle, self.track_mesh, settings)
        return solution

    def calculate_points(
        self, solution: Solution, data: CompetitionData
    ) -> CompetitionPoints:
        t_team = solution.total_time
        t_min = data.autocross_t_min
        points = calculate_points(t_team, t_min, AUTOCROSS_COEFFICIENTS)[1]
        return {"autocross": points}
