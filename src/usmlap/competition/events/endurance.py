"""
This module defines the endurance and efficiency events at Formula Student.
"""

from dataclasses import InitVar, dataclass, field
from math import ceil

from usmlap.simulation import SimulationSettings, Solution, simulate
from usmlap.track import (
    Mesh,
    MeshGenerator,
    TrackData,
    load_track_from_spreadsheet,
)
from usmlap.vehicle import Vehicle, get_new_vehicle
from usmlap.vehicle.parameters import DischargeCurrentLimit

from ..points import (
    EFFICIENCY_COEFFICIENTS,
    ENDURANCE_COEFFICIENTS,
    CompetitionData,
    CompetitionPoints,
    calculate_points,
)
from .event import EventInterface

ENDURANCE_TRACK_LENGTH = 22000


@dataclass
class Endurance(EventInterface, label="endurance"):
    """
    Endurance and efficiency events at Formula Student.
    """

    track_file: InitVar[str]
    track_data: TrackData = field(init=False)

    def __post_init__(self, track_file: str) -> None:
        self.track_data = load_track_from_spreadsheet(track_file)

    def simulate_event(
        self, vehicle: Vehicle, settings: SimulationSettings
    ) -> Solution:
        mesh = self.get_mesh(settings.mesh_resolution)
        vehicle = _modify_vehicle_for_event(vehicle)
        solution = simulate(vehicle, mesh, settings)
        return solution

    def calculate_points(
        self, solution: Solution, data: CompetitionData
    ) -> CompetitionPoints:

        t_team = solution.total_time
        t_min = data.endurance_t_min
        endurance_points = calculate_points(
            t_team, t_min, ENDURANCE_COEFFICIENTS
        )[1]

        energy_used_kwh = solution.total_energy_used / 3.6e6
        ef_team = energy_used_kwh * (solution.total_time**2)
        ef_min = data.efficiency_ef_min
        efficiency_points = calculate_points(
            ef_team, ef_min, EFFICIENCY_COEFFICIENTS
        )[1]

        return {"endurance": endurance_points, "efficiency": efficiency_points}

    def _generate_mesh(self, resolution: float) -> Mesh:
        """
        Generate a track mesh for the endurance event.

        Args:
            resolution (float): The resolution of the mesh.

        Returns:
            mesh (Mesh): A mesh of the track.
        """
        base_mesh = MeshGenerator(resolution).generate_mesh(self.track_data)

        number_of_laps = ceil(ENDURANCE_TRACK_LENGTH / base_mesh.track_length)

        endurance_mesh = base_mesh.get_repeating_mesh(number_of_laps)
        return endurance_mesh


def _modify_vehicle_for_event(vehicle: Vehicle) -> Vehicle:
    """
    Modify a vehicle for the endurance event by updating parameters.
    """
    return get_new_vehicle(vehicle, DischargeCurrentLimit, 0.3)
