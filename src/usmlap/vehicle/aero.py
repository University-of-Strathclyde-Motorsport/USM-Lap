"""
This module models the aerodynamics of a vehicle.
"""

from __future__ import annotations
from .common import Subsystem, AbstractSubsystem
from abc import ABC, abstractmethod
from typing import Literal, Annotated
from annotated_types import Unit
from pydantic import BaseModel, Field
import math


class AeroAttitude(BaseModel):
    """
    Aerodynamic attitude of a vehicle.

    Attributes:
        air_density (float): The density of air.
        velocity (float): The velocity of the vehicle.
        front_ride_height (float): The front ride height of the vehicle.
        rear_ride_height (float): The rear ride height of the vehicle.
        roll_angle (float): The roll angle of the vehicle.
        pitch_angle (float): The pitch angle of the vehicle.
        yaw_angle (float): The yaw angle of the vehicle.
    """

    air_density: float = Field(gt=0)
    velocity: float = Field(ge=0)
    front_ride_height: float = Field(ge=0, default=0)
    rear_ride_height: float = Field(ge=0, default=0)
    roll_angle: float = Field(ge=-math.pi / 2, le=math.pi / 2, default=0)
    pitch_angle: float = Field(ge=-math.pi / 2, le=math.pi / 2, default=0)
    yaw_angle: float = Field(ge=-math.pi / 2, le=math.pi / 2, default=0)


class AeroModelInterface(ABC, AbstractSubsystem):
    """
    Abstract  base class for aero models.
    """

    @abstractmethod
    def get_lift_coefficient(self, attitude: AeroAttitude) -> float: ...

    @abstractmethod
    def get_drag_coefficient(self, attitude: AeroAttitude) -> float: ...


class ConstantAero(AeroModelInterface, type="constant"):
    """
    Constant aero model.

    Lift and drag coefficients do not change with velocity.
    """

    model_type: Literal["constant"]

    lift_coefficient: float = Field(gt=0)
    drag_coefficient: float = Field(gt=0)

    def get_lift_coefficient(self, attitude: AeroAttitude) -> float:
        return self.lift_coefficient

    def get_drag_coefficient(self, attitude: AeroAttitude) -> float:
        return self.drag_coefficient


AeroModel = Annotated[ConstantAero, Field(discriminator="model_type")]


class AeroPackage(Subsystem):
    """
    The aerodynamic package of a vehicle.

    Attributes:
        frontal_area (float): The frontal area of the vehicle.
        aero_model (AeroModel): The aerodynamic model to use.
    """

    frontal_area: Annotated[float, Field(gt=0), Unit("m^2")]
    aero_model: AeroModel

    def get_downforce(self, attitude: AeroAttitude) -> float:
        lift_coefficient = self.aero_model.get_lift_coefficient(attitude)
        return self.calculate_aero_force(lift_coefficient, attitude)

    def get_drag(self, attitude: AeroAttitude) -> float:
        drag_coefficient = self.aero_model.get_drag_coefficient(attitude)
        return self.calculate_aero_force(drag_coefficient, attitude)

    def calculate_aero_force(
        self, coefficient: float, attitude: AeroAttitude
    ) -> float:
        return (
            0.5
            * coefficient
            * self.frontal_area
            * attitude.air_density
            * attitude.velocity**2
        )
