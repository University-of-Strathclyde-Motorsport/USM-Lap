"""
This module defines settings for a simulation."""

from __future__ import annotations

from pathlib import Path
from pprint import pprint
from typing import Annotated

import yaml
from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PlainSerializer,
)

from usmlap.core.filepath import OUTPUT_ROOT
from usmlap.model import GlobalContext, LambdaCoefficients
from usmlap.model.environment import EnvironmentSettings
from usmlap.model.traction import FourCornerModel, PointMass
from usmlap.model.vehicle_model import VehicleModelSettings
from usmlap.solver import QuasiSteadyStateSolver as QSS
from usmlap.solver import QuasiTransientSolver as QT
from usmlap.solver import SolverInterface, SolverRegistry
from usmlap.track.settings import TrackSettings
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
        BeforeValidator(SolverRegistry.ensure_value),
        PlainSerializer(SolverRegistry.get_key, return_type=str),
    ] = QT
    environment: EnvironmentSettings = Field(
        default_factory=EnvironmentSettings
    )
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
    track: TrackSettings
    output_path: Path = OUTPUT_ROOT
    vehicle: VehicleSettings
    boundary_conditions: BoundaryConditionSettings
    environment: EnvironmentSettings

    def get_legacy_settings(self) -> SimulationSettings:
        """Convert to legacy settings object.
        TODO: remove this after finishing migration.
        """
        return SimulationSettings(
            mesh_resolution=self.track.resolution,
            vehicle_model=self.vehicle.vehicle_model,
            solver=self.solver,
            environment=self.environment,
            lambdas=LambdaCoefficients(),
        )

    @staticmethod
    def from_file(filepath: Path) -> SimSettings:
        with open(filepath) as file:
            data = yaml.safe_load(file)
        return SimSettings.model_validate(data)


class VehicleSettings(BaseModel):
    """Settings for the vehicle and vehicle model."""

    vehicle_file: Path
    vehicle_model: VehicleModelSettings = Field(
        default_factory=VehicleModelSettings, exclude=True
    )
    environment: EnvironmentSettings


class BoundaryConditionSettings(BaseModel):
    """Boundary conditions for the simulation."""

    initial_soc: float = Field(gt=0, le=1, default=1)
    initial_cell_temperature: float | None = None  # default to TAmbient
    initial_velocity: float = 0


if __name__ == "__main__":
    filepath = Path(r"sims/basic_simulation.yaml")
    with open(filepath) as file:
        data = yaml.safe_load(file)

    pprint(data)
