"""
This module contains code for running a simulation.
"""

from pydantic import BaseModel, ConfigDict
from vehicle.vehicle import Vehicle
from track.mesh import Mesh
from .environment import Environment
from .model.point_mass import PointMassVehicleModel
from .solver.quasi_steady_state import QuasiSteadyStateSolver


class Simulation(BaseModel):
    """
    A simulation object.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    vehicle: Vehicle
    track: Mesh
    environment: Environment = Environment()
    vehicle_model: PointMassVehicleModel = PointMassVehicleModel()
    solver: QuasiSteadyStateSolver = QuasiSteadyStateSolver()
