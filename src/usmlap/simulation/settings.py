"""
This module defines settings for a simulation."""

from typing import Annotated

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PlainSerializer,
)

from usmlap.model import Environment, GlobalContext, LambdaCoefficients
from usmlap.model.traction import FourCornerModel, PointMass
from usmlap.model.vehicle_model import VehicleModelSettings
from usmlap.solver import QuasiSteadyStateSolver as QSS
from usmlap.solver import QuasiTransientSolver as QT
from usmlap.solver import SolverInterface, SolverRegistry
from usmlap.vehicle import Vehicle


class SimulationSettings(BaseModel):
    """
    Settings for a simulation.

    Attributes:
        environment (Environment): Environmental variables for the simulation.
        vehicle_model (TractionModel): The vehicle model to use.
        solver (SolverInterface): The solver to use.
        lambdas (LambdaCoefficients): Coefficients for the vehicle model.

    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    mesh_resolution: float = 0.1
    vehicle_model: VehicleModelSettings = Field(
        default_factory=VehicleModelSettings, exclude=True
    )
    solver: Annotated[
        type[SolverInterface],
        BeforeValidator(SolverRegistry.get),
        PlainSerializer(SolverRegistry.get_key, return_type=str),
    ] = QT
    environment: Environment = Field(default_factory=Environment)
    lambdas: LambdaCoefficients = Field(default_factory=LambdaCoefficients)

    def get_global_context(self, vehicle: Vehicle) -> GlobalContext:
        return GlobalContext(
            environment=self.environment,
            lambdas=self.lambdas,
            vehicle=vehicle,
        )


class QualityPresets:
    """
    Simulation setting quality presets.

    Attributes:
        DRAFT: Solves very quickly, but accuracy is low.
        FAST: Solves quickly, with decent accuracy.
        HIGH_QUALITY: Solves slowly, with high accuracy.

    """

    DRAFT: SimulationSettings = SimulationSettings(
        mesh_resolution=1,
        vehicle_model=VehicleModelSettings(traction_model=PointMass),
        solver=QSS,
    )
    DRAFT_QT: SimulationSettings = SimulationSettings(
        mesh_resolution=1,
        vehicle_model=VehicleModelSettings(traction_model=PointMass),
        solver=QT,
    )
    FAST: SimulationSettings = SimulationSettings(
        mesh_resolution=0.5,
        vehicle_model=VehicleModelSettings(traction_model=FourCornerModel),
        solver=QT,
    )

    FAST_QSS: SimulationSettings = SimulationSettings(
        mesh_resolution=0.5,
        vehicle_model=VehicleModelSettings(traction_model=FourCornerModel),
        solver=QSS,
    )
    HIGH_QUALITY: SimulationSettings = SimulationSettings(
        mesh_resolution=0.1,
        vehicle_model=VehicleModelSettings(traction_model=FourCornerModel),
        solver=QT,
    )


class SimSettings(BaseModel):
    """Settings for a single simulation."""

    solver: Annotated[
        type[SolverInterface],
        BeforeValidator(SolverRegistry.get),
        PlainSerializer(SolverRegistry.get_key, return_type=str),
    ] = QT
