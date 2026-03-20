"""
This module defines the acceleration event at Formula Student.
"""

from copy import copy
from dataclasses import dataclass

from usmlap.simulation.simulation import SimulationSettings, simulate
from usmlap.simulation.solution import Solution
from usmlap.simulation.solver.quasi_steady_state import QuasiSteadyStateSolver
from usmlap.track.mesh import Mesh, MeshGenerator
from usmlap.track.track_data import load_track_from_spreadsheet
from usmlap.vehicle.vehicle import Vehicle

from ..points import (
    ACCELERATION_COEFFICIENTS,
    CompetitionData,
    CompetitionPoints,
    calculate_points,
)
from .event import EventInterface

ACCELERATION_TRACK = "Acceleration.xlsx"
DEFAULT_MESH_RESOLUTION = 0.1


@dataclass
class Acceleration(EventInterface, label="acceleration"):
    """
    Acceleration event at Formula Student.
    """

    mesh_resolution: float = DEFAULT_MESH_RESOLUTION

    def __post_init__(self) -> None:
        self.track_mesh = _get_acceleration_mesh(self.mesh_resolution)

    def simulate_event(
        self, vehicle: Vehicle, settings: SimulationSettings
    ) -> Solution:
        settings = copy(settings)
        settings.solver = QuasiSteadyStateSolver
        solution = simulate(vehicle, self.track_mesh, settings)
        return solution

    def calculate_points(
        self, solution: Solution, data: CompetitionData
    ) -> CompetitionPoints:
        t_team = solution.total_time
        t_min = data.acceleration_t_min
        points = calculate_points(t_team, t_min, ACCELERATION_COEFFICIENTS)[1]
        return {"acceleration": points}


def _get_acceleration_mesh(resolution: float) -> Mesh:
    """
    Generate a mesh for the acceleration event.

    Returns:
        mesh (Mesh): A mesh of the track.
    """
    track_data = load_track_from_spreadsheet(ACCELERATION_TRACK)
    mesh = MeshGenerator(resolution=resolution).generate_mesh(track_data)
    return mesh
