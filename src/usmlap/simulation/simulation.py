"""
This module contains code for running a simulation.
"""

from pydantic import BaseModel, ConfigDict
from track.mesh import Mesh
from .model.point_mass import PointMassVehicleModel
from .solver.quasi_steady_state import QuasiSteadyStateSolver
from .solution import Solution


class Simulation(BaseModel):
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

    model_config = ConfigDict(arbitrary_types_allowed=True)

    vehicle_model: PointMassVehicleModel
    track: Mesh
    solver: QuasiSteadyStateSolver
    solution: Solution = Solution()

    def solve(self) -> Solution:
        return self.solver.solve()
