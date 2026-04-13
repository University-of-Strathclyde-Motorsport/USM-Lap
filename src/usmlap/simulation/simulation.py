"""
This module contains code for running a simulation.
"""

from __future__ import annotations

from usmlap.track import Mesh
from usmlap.vehicle import Vehicle

from .settings import SimulationSettings
from .solution import Solution, create_new_solution


def simulate(
    vehicle: Vehicle, track_mesh: Mesh, settings: SimulationSettings
) -> Solution:
    """
    Simulate a vehicle driving around a track.

    Args:
        vehicle (Vehicle): The vehicle to simulate.
        settings (SimulationSettings): Settings for the simulation.
    """
    vehicle_model = settings.vehicle_model()
    global_context = settings.get_global_context(vehicle)
    solver = settings.solver(vehicle_model, global_context)

    solution = create_new_solution(track_mesh, vehicle_model)
    return solver.solve(solution)
