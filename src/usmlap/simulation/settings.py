"""
This module defines settings for a simulation.
"""

from dataclasses import dataclass, field

from usmlap.model import Environment, GlobalContext, LambdaCoefficients
from usmlap.model.traction import FourCornerModel, PointMass
from usmlap.model.vehicle_model import VehicleModelSettings
from usmlap.solver import QuasiSteadyStateSolver as QSS
from usmlap.solver import QuasiTransientSolver as QT
from usmlap.solver import SolverInterface
from usmlap.track.mesh_generation import Resolution
from usmlap.vehicle import Vehicle


@dataclass()
class SimulationSettings(object):
    """
    Settings for a simulation.

    Attributes:
        environment (Environment): Environmental variables for the simulation.
        vehicle_model (TractionModel): The vehicle model to use.
        solver (SolverInterface): The solver to use.
        lambdas (LambdaCoefficients): Coefficients for the vehicle model.
    """

    mesh_resolution: Resolution = Resolution(0.1)
    vehicle_model: VehicleModelSettings = field(
        default_factory=VehicleModelSettings
    )
    solver: type[SolverInterface] = QT
    environment: Environment = field(default_factory=Environment)
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
        mesh_resolution=Resolution(1),
        vehicle_model=VehicleModelSettings(traction_model=PointMass),
        solver=QSS,
    )
    DRAFT_QT: SimulationSettings = SimulationSettings(
        mesh_resolution=Resolution(1),
        vehicle_model=VehicleModelSettings(traction_model=PointMass),
        solver=QT,
    )
    FAST: SimulationSettings = SimulationSettings(
        mesh_resolution=Resolution(0.5),
        vehicle_model=VehicleModelSettings(traction_model=FourCornerModel),
        solver=QT,
    )

    FAST_QSS: SimulationSettings = SimulationSettings(
        mesh_resolution=Resolution(0.5),
        vehicle_model=VehicleModelSettings(traction_model=FourCornerModel),
        solver=QSS,
    )
    HIGH_QUALITY: SimulationSettings = SimulationSettings(
        mesh_resolution=Resolution(0.1),
        vehicle_model=VehicleModelSettings(traction_model=FourCornerModel),
        solver=QT,
    )
