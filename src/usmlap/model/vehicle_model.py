"""
This module implements the vehicle model, which contains all the subsystem models.
"""

from dataclasses import dataclass

from .powertrain import PowertrainModelInterface, SingleMotorRWD
from .traction import FourCornerModel, TractionModel
from .tyre import (
    CombinedTyreModel,
    FrictionEllipse,
    LinearTyre,
    PureTyreModel,
    TyreModel,
)


@dataclass
class VehicleModel(object):
    """Dataclass to store all the models used for modelling a vehicle."""

    powertrain: PowertrainModelInterface
    traction: TractionModel


@dataclass
class VehicleModelSettings(object):
    """Configuration options for the vehicle model."""

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
