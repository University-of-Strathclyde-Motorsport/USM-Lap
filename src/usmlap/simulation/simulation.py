"""
This module contains code for running a simulation.
"""

from __future__ import annotations
from vehicle.vehicle import Vehicle
from simulation.environment import Environment
from .model.vehicle_model import VehicleModelInterface
from .model.point_mass import PointMassVehicleModel
from .solver.solver_interface import SolverInterface
from .solver.quasi_steady_state import QuasiSteadyStateSolver
from .solution import Solution
from track.mesh import Mesh


class Simulation(object):
    """
    A simulation object.

    Attributes:
        vehicle (Vehicle): The vehicle to simulate.
        track (Mesh): The track to simulate.
        environment (Environment): Environmental variables for the simulation.
        vehicle_model (VehicleModelInterface): The vehicle model to use.
        solver (SolverInterface): The solver to use.
        solution (Solution): The results of the simulation.
    """

    solver: SolverInterface

    def __init__(
        self,
        vehicle: Vehicle,
        track: Mesh,
        environment: Environment = Environment(),
        vehicle_model: type[VehicleModelInterface] = PointMassVehicleModel,
        solver: type[SolverInterface] = QuasiSteadyStateSolver,
    ) -> None:
        self.solver = solver(
            vehicle_model=vehicle_model(
                vehicle=vehicle, environment=environment
            ),
            track_mesh=track,
        )

    def simulate(self) -> Solution:
        return self.solver.solve()
