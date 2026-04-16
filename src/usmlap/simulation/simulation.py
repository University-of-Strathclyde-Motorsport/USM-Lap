"""
This module contains code for running a simulation.
"""

from __future__ import annotations

from pyparsing import Optional

from usmlap.model import StateVariables
from usmlap.track import Mesh
from usmlap.vehicle import Vehicle

from .settings import SimulationSettings
from .solution import Solution, create_new_solution


def simulate(
    vehicle: Vehicle,
    track_mesh: Mesh,
    settings: SimulationSettings,
    initial_state: Optional[StateVariables] = None,
) -> Solution:
    """
    Simulate a vehicle driving around a track.

    Args:
        vehicle (Vehicle): The vehicle to simulate.
        settings (SimulationSettings): Settings for the simulation.
    """
    if initial_state is None:
        initial_state = StateVariables.get_default()

    vehicle_model = settings.vehicle_model()
    global_context = settings.get_global_context(vehicle)
    solver = settings.solver(vehicle_model, global_context)

    solution = create_new_solution(track_mesh, vehicle_model, initial_state)
    return solver.solve(solution)
