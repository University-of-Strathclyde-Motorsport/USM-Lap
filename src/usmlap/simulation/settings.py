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
    mesh_resolution: float = 0.1
    vehicle_model: type[VehicleModelInterface] = PointMass
    solver: type[SolverInterface] = QT
    lambdas: LambdaCoefficients = field(default_factory=LambdaCoefficients)


class QualityPresets(object):
    """
    Simulation setting quality presets.

    Attributes:
        DRAFT: Solves very quickly, but accuracy is low.
        FAST: Solves quickly, with decent accuracy.
        HIGH_QUALITY: Solves slowly, with high accuracy.
    """

    DRAFT: SimulationSettings = SimulationSettings(
        mesh_resolution=2, vehicle_model=PointMass, solver=QSS
    )
    FAST: SimulationSettings = SimulationSettings(
        mesh_resolution=0.5, vehicle_model=PointMass, solver=QT
    )
    HIGH_QUALITY: SimulationSettings = SimulationSettings(
        mesh_resolution=0.1, vehicle_model=PointMass, solver=QT
    )
