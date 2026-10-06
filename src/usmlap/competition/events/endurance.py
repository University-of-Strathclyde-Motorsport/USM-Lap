"""
This module defines the endurance and efficiency events at Formula Student.
"""

from dataclasses import dataclass
from math import ceil
from pathlib import Path

from usmlap.competition.events.event import EventInterface
from usmlap.competition.points import (
    EFFICIENCY_COEFFICIENTS,
    ENDURANCE_COEFFICIENTS,
    CompetitionData,
    CompetitionPoints,
    calculate_points,
)
from usmlap.simulation.settings import SimulationSettings
from usmlap.simulation.simulation import simulate
from usmlap.telemetry.data.solution import TelemetrySolution
from usmlap.track.mesh import Mesh
from usmlap.track.mesh_generation import generate_mesh
from usmlap.track.settings import TrackSettings
from usmlap.vehicle.parameters import DischargeCurrentLimit, get_new_vehicle
from usmlap.vehicle.vehicle import Vehicle

ENDURANCE_TRACK_LENGTH: float = 22000
DEFAULT_DISCHARGE_LIMIT: float = 0.4


@dataclass
class Endurance(EventInterface, label="endurance"):
    """
    Endurance and efficiency events at Formula Student.
    """

    track_file: Path
    simulate_efficiency: bool = True

    def simulate_event(
        self,
        vehicle: Vehicle,
        settings: SimulationSettings,
    ) -> TelemetrySolution:
        mesh = self.get_mesh(settings.mesh_resolution)
        vehicle = _modify_vehicle_for_event(vehicle)
        solution = simulate(vehicle, mesh, settings)
        return solution

    def calculate_points(
        self,
        solution: TelemetrySolution,
        data: CompetitionData,
    ) -> CompetitionPoints:

        t_team = solution.solution.total_time
        t_min = data.endurance_t_min
        endurance_points = calculate_points(
            t_team,
            t_min,
            ENDURANCE_COEFFICIENTS,
        )[1]
        points = {"endurance": endurance_points}

        if self.simulate_efficiency:
            energy_used_kwh = solution.solution.total_energy_used / 3.6e6
            ef_team = energy_used_kwh * (solution.solution.total_time**2)
            ef_min = data.efficiency_ef_min
            efficiency_points = calculate_points(
                ef_team,
                ef_min,
                EFFICIENCY_COEFFICIENTS,
            )[1]
            points["efficiency"] = efficiency_points

        return points

    def _generate_mesh(self, resolution: float) -> Mesh:
        """
        Generate a track mesh for the endurance event.

        Args:
            resolution (float): The resolution of the mesh.

        Returns:
            mesh (Mesh): A mesh of the track.

        """
        base_mesh = generate_mesh(
            TrackSettings(track_file=self.track_file, resolution=resolution)
        )

        number_of_laps = ceil(ENDURANCE_TRACK_LENGTH / base_mesh.track_length)

        endurance_mesh = base_mesh.get_repeating_mesh(number_of_laps)
        return endurance_mesh


def _modify_vehicle_for_event(vehicle: Vehicle) -> Vehicle:
    """
    Modify a vehicle for the endurance event by updating parameters.
    """
    return get_new_vehicle(
        vehicle,
        DischargeCurrentLimit,
        DEFAULT_DISCHARGE_LIMIT,
    )
