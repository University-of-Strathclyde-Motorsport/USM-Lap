"""
This module implements the vehicle model,
which contains all the subsystem models.
"""

from dataclasses import dataclass

from usmlap.model.powertrain.interface import PowertrainModelInterface
from usmlap.model.powertrain.single_motor_rwd import SingleMotorRWD
from usmlap.model.traction.four_corner import FourCornerModel
from usmlap.model.traction.traction_model import TractionModel
from usmlap.model.tyre.combined.friction_ellipse import FrictionEllipse
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


@dataclass
class VehicleModelSettings:
    """
    Configuration options for the vehicle model."""

    powertrain: type[PowertrainModelInterface] = SingleMotorRWD
    traction_model: type[TractionModel] = FourCornerModel
    longitudinal_tyre: type[PureTyreModel] = LinearTyre
    lateral_tyre: type[PureTyreModel] = LinearTyre
    combined_tyre: type[CombinedTyreModel] = FrictionEllipse

    def build_vehicle_model(self) -> VehicleModel:
        tyre_model = TyreModel(
            longitudinal=self.longitudinal_tyre(),
            lateral=self.lateral_tyre(),
            combined=self.combined_tyre(),
        )
        powertrain = self.powertrain()
        traction = self.traction_model(powertrain, tyre_model)
        return VehicleModel(powertrain=powertrain, traction=traction)
