"""
This module contains code for running a simulation.
"""

from vehicle.vehicle import Vehicle
from simulation.environment import Environment
from track.mesh import Mesh
from .model.vehicle_model import VehicleModelInterface
from .solver.solver_interface import SolverInterface
from .solution import Solution


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
        environment: Environment,
        vehicle_model: type[VehicleModelInterface],
        track: Mesh,
        solver: type[SolverInterface],
    ) -> None:
        self.solver = solver(
            vehicle_model=vehicle_model(
                vehicle=vehicle, environment=environment
            ),
            track_mesh=track,
        )

    def simulate(self) -> Solution:
        return self.solver.solve()
