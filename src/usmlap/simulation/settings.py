"""
This module defines settings for a simulation.
"""

from dataclasses import dataclass, field

from usmlap.model import (
    Environment,
    GlobalContext,
    LambdaCoefficients,
    VehicleModelInterface,
)
from usmlap.model.vehicle import Bicycle, PointMass
from usmlap.track.mesh_generation import Resolution
from usmlap.vehicle import Vehicle

from .solver import QuasiSteadyStateSolver as QSS
from .solver import QuasiTransientSolver as QT
from .solver import SolverInterface


@dataclass(frozen=True)
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
    mesh_resolution: Resolution = Resolution(0.1)
    vehicle_model: type[VehicleModelInterface] = PointMass
    solver: type[SolverInterface] = QT
    lambdas: LambdaCoefficients = field(default_factory=LambdaCoefficients)

    def get_global_context(self, vehicle: Vehicle) -> GlobalContext:
        return GlobalContext(
            environment=self.environment, lambdas=self.lambdas, vehicle=vehicle
        )


class QualityPresets(object):
    """
    Simulation setting quality presets.

    Attributes:
        DRAFT: Solves very quickly, but accuracy is low.
        FAST: Solves quickly, with decent accuracy.
        HIGH_QUALITY: Solves slowly, with high accuracy.
    """

    DRAFT: SimulationSettings = SimulationSettings(
        mesh_resolution=Resolution(1), vehicle_model=PointMass, solver=QSS
    )
    FAST: SimulationSettings = SimulationSettings(
        mesh_resolution=Resolution(0.5), vehicle_model=Bicycle, solver=QT
    )
    HIGH_QUALITY: SimulationSettings = SimulationSettings(
        mesh_resolution=Resolution(0.1), vehicle_model=Bicycle, solver=QT
    )
