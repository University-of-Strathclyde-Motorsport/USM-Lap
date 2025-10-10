"""
This module implements a quasi-steady-state solver.
"""

from .solver_interface import SolverInterface
from vehicle.vehicle import Vehicle
from track.mesh import Node


class QuasiSteadyStateSolver(SolverInterface):
    """
    Quasi-steady-state solver.
    """

    def solve_node(self, vehicle: Vehicle, node: Node) -> None:
        pass
