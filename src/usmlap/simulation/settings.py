"""
This module defines settings for a simulation."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from pydantic import (
    BaseModel,
    BeforeValidator,
    Field,
    PlainSerializer,
    computed_field,
)

from usmlap.core.filepath import OUTPUT_ROOT
from usmlap.core.git_tools import get_git_hash
from usmlap.core.library import SupportsLoading
from usmlap.model.context import GlobalContext
from usmlap.model.environment import EnvironmentSettings
from usmlap.model.lambda_coefficients import LambdaCoefficients
from usmlap.model.vehicle_model import VehicleModelSettings
from usmlap.plot.generate_plots import PlotSettings
from usmlap.solver import QuasiTransientSolver as QT
from usmlap.solver import SolverInterface, SolverRegistry
from usmlap.track.settings import TrackSettings
from usmlap.vehicle.vehicle import Vehicle


class SimSettings(SupportsLoading):
    """Settings for a single simulation."""

    sim_name: str = ""
    solver: Annotated[
        type[SolverInterface],
        BeforeValidator(SolverRegistry.ensure_value),
        PlainSerializer(SolverRegistry.get_key, return_type=str),
    ] = QT
    track: TrackSettings
    output_path: Path = OUTPUT_ROOT
    vehicle: VehicleSettings
    boundary_conditions: BoundaryConditionSettings
    plots: PlotSettings = Field(default_factory=PlotSettings)

    @computed_field
    def git_version(self) -> str:
        return get_git_hash()

    def get_global_context(self, vehicle: Vehicle) -> GlobalContext:
        # TODO: remove this
        return GlobalContext(
            environment=self.vehicle.environment,
            lambdas=self.vehicle.lambdas,
            vehicle=vehicle,
        )


class VehicleSettings(BaseModel):
    """Settings for the vehicle and vehicle model."""

    vehicle_file: Path
    vehicle_model: VehicleModelSettings = Field(
        default_factory=VehicleModelSettings
    )
    environment: EnvironmentSettings
    lambdas: LambdaCoefficients


class BoundaryConditionSettings(BaseModel):
    """Boundary conditions for the simulation."""

    initial_soc: float = Field(gt=0, le=1, default=1)
    initial_cell_temperature: float | None = None  # default to TAmbient
    initial_velocity: float = 0
