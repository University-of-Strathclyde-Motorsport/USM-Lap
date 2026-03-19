"""
This module defines the skidpad event at Formula Student.
"""

import math
from copy import copy
from dataclasses import dataclass, field
from enum import IntEnum

from usmlap.simulation.environment import Environment
from usmlap.simulation.model.point_mass import PointMassVehicleModel
from usmlap.simulation.model.vehicle_model import VehicleModelInterface
from usmlap.simulation.simulation import SimulationSettings, simulate
from usmlap.simulation.solver.quasi_steady_state import QuasiSteadyStateSolver
from usmlap.simulation.vehicle_state import StateVariables
from usmlap.track.mesh import Mesh, TrackNode
from usmlap.track.track_data import Configuration
from usmlap.vehicle.vehicle import Vehicle

from ..points import (
    SKIDPAD_COEFFICIENTS,
    CompetitionData,
    CompetitionPoints,
    calculate_points,
)
from .event import EventInterface

SKIDPAD_TRACK = "Skidpad.xlsx"
SKIDPAD_RADIUS = 9.125
RUNUP_DISTANCE = 5
DEFAULT_MESH_RESOLUTION = 0.1


class SkidpadSector(IntEnum):
    """
    Enum defining sectors of the skidpad track.
    """

    RUNUP = 1
    RIGHT_ENTRY = 2
    RIGHT_TIMED = 3
    LEFT_ENTRY = 4
    LEFT_TIMED = 5


@dataclass
class Skidpad(EventInterface, label="skidpad"):
    """
    Skidpad event at Formula Student.
    """

    competition_data: CompetitionData
    vehicle_model: type[VehicleModelInterface] = PointMassVehicleModel
    mesh_resolution: float = DEFAULT_MESH_RESOLUTION
    track_mesh: Mesh = field(init=False)
    vehicle_state_variables: StateVariables = field(init=False)

    def __post_init__(self) -> None:
        self.track_mesh = _get_skidpad_mesh(self.mesh_resolution)
        self.vehicle_state_variables = StateVariables()

    def simulate_event(self, vehicle: Vehicle) -> CompetitionPoints:

        simulation_settings = SimulationSettings(
            environment=Environment(),
            vehicle_model=self.vehicle_model,
            solver=QuasiSteadyStateSolver,
        )

        solution = simulate(vehicle, self.track_mesh, simulation_settings)

        right_time = solution.get_sector_time(SkidpadSector.RIGHT_TIMED)
        left_time = solution.get_sector_time(SkidpadSector.LEFT_TIMED)
        t_team = (right_time + left_time) / 2
        t_min = self.competition_data.skidpad_t_min
        print(f"t_team: {t_team} s, t_min: {t_min} s")
        points = calculate_points(t_team, t_min, SKIDPAD_COEFFICIENTS)[1]
        return {"skidpad": points}


def _get_skidpad_mesh(resolution: float) -> Mesh:
    """
    Get a track mesh for the skidpad event.

    The track has 5 sectors:
        1. Runup
        2. Right circle lap 1 (untimed)
        3. Right circle lap 2 (timed)
        4. Left circle lap 1 (untimed)
        5. Left circle lap 2 (timed)

    Returns:
        mesh (Mesh): A mesh of the skidpad track.
    """

    runup_length = RUNUP_DISTANCE
    runup_node_count = math.ceil(runup_length / resolution)
    runup_node_length = runup_length / runup_node_count

    curvature = 1 / SKIDPAD_RADIUS
    circle_length = 2 * math.pi * SKIDPAD_RADIUS
    circle_node_count = math.ceil(circle_length / resolution)
    circle_node_length = circle_length / circle_node_count

    runup_node = TrackNode(
        position=0,
        length=runup_node_length,
        curvature=0,
        elevation=0,
        sector=SkidpadSector.RUNUP,
    )
    right_entry_node = TrackNode(
        position=0,
        length=circle_node_length,
        curvature=-curvature,
        elevation=0,
        sector=SkidpadSector.RIGHT_ENTRY,
    )
    right_timed_node = TrackNode(
        position=0,
        length=circle_node_length,
        curvature=-curvature,
        elevation=0,
        sector=SkidpadSector.RIGHT_TIMED,
    )
    left_entry_node = TrackNode(
        position=0,
        length=circle_node_length,
        curvature=curvature,
        elevation=0,
        sector=SkidpadSector.LEFT_ENTRY,
    )
    left_timed_node = TrackNode(
        position=0,
        length=circle_node_length,
        curvature=curvature,
        elevation=0,
        sector=SkidpadSector.LEFT_TIMED,
    )

    nodes = [
        *[copy(runup_node) for _ in range(runup_node_count)],
        *[copy(right_entry_node) for _ in range(circle_node_count)],
        *[copy(right_timed_node) for _ in range(circle_node_count)],
        *[copy(left_entry_node) for _ in range(circle_node_count)],
        *[copy(left_timed_node) for _ in range(circle_node_count)],
    ]

    mesh = Mesh(nodes=nodes, configuration=Configuration.OPEN)
    return mesh
