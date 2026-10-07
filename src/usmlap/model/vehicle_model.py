"""
This module implements the vehicle model,
which contains all the subsystem models.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field, PlainSerializer

from usmlap.model.powertrain import PowertrainModelRegistry
from usmlap.model.powertrain.interface import PowertrainModelInterface
from usmlap.model.powertrain.single_motor_rwd import SingleMotorRWD
from usmlap.model.traction import TractionModelRegistry
from usmlap.model.traction.four_corner import FourCornerModel
from usmlap.model.traction.traction_model import TractionModel
from usmlap.model.tyre.combined import CombinedTyreModelRegistry
from usmlap.model.tyre.combined.friction_ellipse import FrictionEllipse
from usmlap.model.tyre.pure import PureTyreModelRegistry
from usmlap.model.tyre.pure.linear import LinearTyre
from usmlap.model.tyre.tyre_model import (
    CombinedTyreModel,
    PureTyreModel,
    TyreModel,
)


@dataclass
class VehicleModel:
    """
    Dataclass to store all the models used for modelling a vehicle."""

    powertrain: PowertrainModelInterface
    traction: TractionModel


class TyreModelSettings(BaseModel):
    """Configuration options for the tyre model."""

    longitudinal: Annotated[
        type[PureTyreModel],
        BeforeValidator(PureTyreModelRegistry.ensure_value),
        PlainSerializer(PureTyreModelRegistry.get_key),
    ] = LinearTyre

    lateral: Annotated[
        type[PureTyreModel],
        BeforeValidator(PureTyreModelRegistry.ensure_value),
        PlainSerializer(PureTyreModelRegistry.get_key),
    ] = LinearTyre

    combined: Annotated[
        type[CombinedTyreModel],
        BeforeValidator(CombinedTyreModelRegistry.ensure_value),
        PlainSerializer(CombinedTyreModelRegistry.get_key),
    ] = FrictionEllipse

    def build_tyre_model(self) -> TyreModel:
        return TyreModel(
            longitudinal=self.longitudinal(),
            lateral=self.lateral(),
            combined=self.combined(),
        )


class VehicleModelSettings(BaseModel):
    """Configuration options for the vehicle model."""

    powertrain: Annotated[
        type[PowertrainModelInterface],
        BeforeValidator(PowertrainModelRegistry.ensure_value),
        PlainSerializer(PowertrainModelRegistry.get_key, return_type=str),
    ] = SingleMotorRWD

    traction: Annotated[
        type[TractionModel],
        BeforeValidator(TractionModelRegistry.ensure_value),
        PlainSerializer(TractionModelRegistry.get_key, return_type=str),
    ] = FourCornerModel

    tyre: TyreModelSettings = Field(default_factory=TyreModelSettings)

    def build_vehicle_model(self) -> VehicleModel:
        tyre_model = self.tyre.build_tyre_model()
        powertrain = self.powertrain()
        traction = self.traction(powertrain, tyre_model)
        return VehicleModel(powertrain=powertrain, traction=traction)
