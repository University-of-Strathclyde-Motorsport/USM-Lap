"""
This module contains code for running a simulation.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from usmlap.simulation.solver import QuasiTransientSolver
from usmlap.track import Mesh
from usmlap.vehicle import Vehicle

from .environment import Environment
from .lambda_coefficients import LambdaCoefficients
from .model.point_mass import PointMassVehicleModel
from .model.vehicle_model import VehicleModelInterface
from .solution import Solution, create_new_solution
from .solver.solver_interface import SolverInterface

MAXIMUM_TRANSIENT_ITERATIONS = 100


@dataclass
class SimulationSettings(object):
    """
    Settings for a simulation.

    Attributes:
        environment (Environment): Environmental variables for the simulation.
        vehicle_model (VehicleModelInterface): The vehicle model to use.
        solver (SolverInterface): The solver to use.
    """

    environment: Environment = field(default_factory=Environment)
    vehicle_model: type[VehicleModelInterface] = PointMassVehicleModel
    solver: type[SolverInterface] = QuasiTransientSolver
    lambdas: LambdaCoefficients = field(default_factory=LambdaCoefficients)


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
        vehicle=vehicle,
        environment=settings.environment,
        lambdas=settings.lambdas,
    )
    solver = settings.solver()
    solution = create_new_solution(track_mesh, vehicle_model)
    return solver.solve(solution)
