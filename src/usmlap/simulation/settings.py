"""
This module defines settings for a simulation.
"""

from dataclasses import dataclass, field

from .environment import Environment
from .lambda_coefficients import LambdaCoefficients
from .model import PointMassVehicleModel as PointMass
from .model import VehicleModelInterface
from .solver import QuasiSteadyStateSolver as QSS
from .solver import QuasiTransientSolver as QT
from .solver import SolverInterface


@dataclass
class SimulationSettings(object):
    """
    Settings for a simulation.

    Attributes:
        environment (Environment): Environmental variables for the simulation.
        vehicle_model (VehicleModelInterface): The vehicle model to use.
        solver (SolverInterface): The solver to use.
        lambdas (LambdaCoefficients): Coefficients for the vehicle model.
    """

    environment: Environment = field(default_factory=Environment)
    vehicle_model: type[VehicleModelInterface] = PointMass
    solver: type[SolverInterface] = QT
    lambdas: LambdaCoefficients = field(default_factory=LambdaCoefficients)


class Presets(object):
    """
    Simulation setting presets.
    """

    DRAFT = SimulationSettings(vehicle_model=PointMass, solver=QSS)
    QUALITY = SimulationSettings(vehicle_model=PointMass, solver=QT)
