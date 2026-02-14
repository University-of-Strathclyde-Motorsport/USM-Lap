"""
This module contains code for running a simulation.
"""

from __future__ import annotations

from pydantic import BaseModel

from simulation.environment import Environment
from track.mesh import Mesh
from vehicle.vehicle import Vehicle

from .model.point_mass import PointMassVehicleModel
from .model.vehicle_model import VehicleModelInterface
from .solution import Solution, create_new_solution
from .solver.quasi_steady_state import QuasiSteadyStateSolver
from .solver.solver_interface import SolverInterface

MAXIMUM_TRANSIENT_ITERATIONS = 100


class SimulationSettings(BaseModel):
    """
    Settings for a simulation.

    Attributes:
        track (Mesh): The track to simulate.
        environment (Environment): Environmental variables for the simulation.
        vehicle_model (VehicleModelInterface): The vehicle model to use.
        solver (SolverInterface): The solver to use.
    """

    environment: Environment = Environment()
    vehicle_model: type[VehicleModelInterface] = PointMassVehicleModel
    solver: type[SolverInterface] = QuasiSteadyStateSolver


def simulate(
    vehicle: Vehicle, track_mesh: Mesh, settings: SimulationSettings
) -> Solution:
    """
    Simulate a vehicle driving around a track.

    Args:
        vehicle (Vehicle): The vehicle to simulate.
        settings (SimulationSettings): Settings for the simulation.
    """
    vehicle_model = settings.vehicle_model(
        vehicle=vehicle, environment=settings.environment
    )
    solver = settings.solver()
    solution = create_new_solution(track_mesh, vehicle_model)
    return solver.solve(solution)
