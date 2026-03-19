"""
This module defines the endurance and efficiency events at Formula Student.
"""

from dataclasses import InitVar, dataclass, field
from math import ceil
from typing import Optional

from usmlap.simulation.environment import Environment
from usmlap.simulation.model.point_mass import PointMassVehicleModel
from usmlap.simulation.model.vehicle_model import VehicleModelInterface
from usmlap.simulation.simulation import SimulationSettings, simulate
from usmlap.simulation.solver.quasi_transient import QuasiTransientSolver
from usmlap.track.mesh import Mesh, MeshGenerator
from usmlap.track.track_data import TrackData, load_track_from_spreadsheet
from usmlap.vehicle.parameters import DischargeCurrentLimit, get_new_vehicle
from usmlap.vehicle.vehicle import Vehicle

from ..points import (
    EFFICIENCY_COEFFICIENTS,
    ENDURANCE_COEFFICIENTS,
    CompetitionData,
    CompetitionPoints,
    calculate_points,
)
from .event import EventInterface

ENDURANCE_TRACK_LENGTH = 22000
DEFAULT_VEHICLE_MODEL = PointMassVehicleModel
DEFAULT_MESH_RESOLUTION = 1


@dataclass
class Endurance(EventInterface, label="endurance"):
    """
    Endurance and efficiency events at Formula Student.
    """

    competition_data: CompetitionData
    track_file: InitVar[str]
    vehicle_model: type[VehicleModelInterface] = DEFAULT_VEHICLE_MODEL
    mesh_resolution: float = DEFAULT_MESH_RESOLUTION
    track_mesh: Mesh = field(init=False)

    def __post_init__(self, track_file: str) -> None:
        track_data = load_track_from_spreadsheet(track_file)
        self.track_mesh = _generate_endurance_mesh(
            track_data, self.mesh_resolution
        )

    def simulate_event(self, vehicle: Vehicle) -> CompetitionPoints:

        vehicle = _modify_vehicle_for_event(vehicle)

        simulation_settings = SimulationSettings(
            environment=Environment(),
            vehicle_model=self.vehicle_model,
            solver=QuasiTransientSolver,
        )

        solution = simulate(vehicle, self.track_mesh, simulation_settings)

        t_team = solution.total_time
        t_min = self.competition_data.endurance_t_min
        endurance_points = calculate_points(
            t_team, t_min, ENDURANCE_COEFFICIENTS
        )[1]

        energy_used_kwh = solution.total_energy_used / 3.6e6
        ef_team = energy_used_kwh * (solution.total_time**2)
        ef_min = self.competition_data.efficiency_ef_min
        efficiency_points = calculate_points(
            ef_team, ef_min, EFFICIENCY_COEFFICIENTS
        )[1]

        return {"endurance": endurance_points, "efficiency": efficiency_points}


def _generate_endurance_mesh(
    track_data: TrackData,
    resolution: float,
    number_of_laps: Optional[int] = None,
) -> Mesh:
    """
    Generate a mesh for the endurance event.
    """
    base_mesh = MeshGenerator(resolution).generate_mesh(track_data)

    if not number_of_laps:
        number_of_laps = ceil(ENDURANCE_TRACK_LENGTH / base_mesh.track_length)

    endurance_mesh = base_mesh.get_repeating_mesh(number_of_laps)
    return endurance_mesh


def _modify_vehicle_for_event(vehicle: Vehicle) -> Vehicle:
    """
    Modify a vehicle for the endurance event by updating parameters.
    """
    return get_new_vehicle(vehicle, DischargeCurrentLimit, 0.3)
