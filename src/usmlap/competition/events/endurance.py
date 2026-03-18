"""
This module defines the endurance and efficiency events at Formula Student.
"""

from math import ceil

from usmlap.simulation.solution import Solution
from usmlap.track.mesh import Mesh, MeshGenerator
from usmlap.vehicle.parameters import DischargeCurrentLimit, get_new_vehicle
from usmlap.vehicle.vehicle import Vehicle

from ..points import (
    EFFICIENCY_COEFFICIENTS,
    ENDURANCE_COEFFICIENTS,
    CompetitionData,
    calculate_points,
)
from .event import EventInterface

ENDURANCE_TRACK_LENGTH = 22000


class Endurance(EventInterface, label="endurance"):
    """
    Endurance and efficiency events at Formula Student.
    """

    def __init__(self, track_file: str) -> None:
        super().__init__(track_file)

    def generate_mesh(self) -> Mesh:
        """
        Overwrite mesh generation to repeat the track for the endurance event.
        """
        base_mesh = MeshGenerator(resolution=1).generate_mesh(self.track_data)
        number_of_laps = ceil(ENDURANCE_TRACK_LENGTH / base_mesh.track_length)
        endurance_mesh = base_mesh.get_repeating_mesh(number_of_laps)
        return endurance_mesh

    def modify_vehicle_for_event(self, vehicle: Vehicle) -> Vehicle:
        return get_new_vehicle(vehicle, DischargeCurrentLimit, 0.3)

    def calculate_points(
        self, solution: Solution, competition_data: CompetitionData
    ) -> dict[str, float]:

        t_team = solution.total_time
        t_min = competition_data.endurance_t_min
        endurance = calculate_points(t_team, t_min, ENDURANCE_COEFFICIENTS)

        ef_team = solution.total_energy_used * (solution.total_time**2)
        ef_min = competition_data.efficiency_ef_min
        efficiency = calculate_points(ef_team, ef_min, EFFICIENCY_COEFFICIENTS)

        return {endurance[0]: endurance[1], efficiency[0]: efficiency[1]}
