"""
This module implements the vehicle model, which contains all the subsystem models.
"""

from dataclasses import dataclass

from .powertrain import PowertrainModelInterface, SingleMotorRWD
from .traction import FourCornerModel, TractionModel


@dataclass
class VehicleModelSettings(object):
    powertrain: type[PowertrainModelInterface] = SingleMotorRWD
    traction_model: type[TractionModel] = FourCornerModel


@dataclass
class VehicleModel(object):
    """Dataclass to store all the models used for modelling a vehicle."""

    powertrain: PowertrainModelInterface
    traction: TractionModel

