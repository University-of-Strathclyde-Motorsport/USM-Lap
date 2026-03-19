"""
This module defines the skidpad event at Formula Student.
"""

import math
from dataclasses import dataclass, field

from usmlap.simulation.environment import Environment
from usmlap.simulation.model.point_mass import PointMassVehicleModel
from usmlap.simulation.model.vehicle_model import VehicleModelInterface
from usmlap.simulation.solver.apex_velocity import solve_apex_velocity
from usmlap.simulation.vehicle_state import StateVariables
from usmlap.track.mesh import TrackNode
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


@dataclass
class Skidpad(EventInterface, label="skidpad"):
    """
    Skidpad event at Formula Student.
    """

    competition_data: CompetitionData
    vehicle_model: type[VehicleModelInterface] = PointMassVehicleModel
    track_node: TrackNode = field(init=False)
    vehicle_state_variables: StateVariables = field(init=False)

    def __post_init__(self) -> None:
        self.track_node = _get_skidpad_node()
        self.vehicle_state_variables = StateVariables()

    def simulate_event(self, vehicle: Vehicle) -> CompetitionPoints:

        vehicle_model = self.vehicle_model(vehicle, environment=Environment())

        velocity = solve_apex_velocity(
            vehicle_model=vehicle_model,
            state_variables=self.vehicle_state_variables,
            node=self.track_node,
        )

        t_team = self.track_node.length / velocity
        t_min = self.competition_data.skidpad_t_min
        points = calculate_points(t_team, t_min, SKIDPAD_COEFFICIENTS)[1]
        return {"skidpad": points}


def _get_skidpad_node() -> TrackNode:
    """
    Get a track node for the skidpad event.

    Returns:
        track_node (TrackNode): The track node.
    """
    track_node = TrackNode(
        position=0,
        length=(2 * math.pi * SKIDPAD_RADIUS),
        curvature=(1 / SKIDPAD_RADIUS),
        elevation=0,
        inclination=0,
        banking=0,
        grip_factor=1,
    )
    return track_node
