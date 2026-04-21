"""
This module implements the vehicle model, which contains all the subsystem models.
"""

from dataclasses import dataclass

from usmlap.model.tyre.pure import PureTyreModel

from .powertrain import PowertrainModelInterface, SingleMotorRWD
from .traction import FourCornerModel, TractionModel
from .tyre import CombinedTyreModel, FrictionEllipse, LinearTyre


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
    # tyre_model: type[TyreModel] = LinearTyre
    longitudinal_tyre: type[PureTyreModel] = LinearTyre
    lateral_tyre: type[PureTyreModel] = LinearTyre
    combined_tyre: type[CombinedTyreModel] = FrictionEllipse

    def build_vehicle_model(self) -> VehicleModel:
        powertrain = self.powertrain()
        traction = self.traction_model(powertrain)
        return VehicleModel(powertrain=powertrain, traction=traction)
