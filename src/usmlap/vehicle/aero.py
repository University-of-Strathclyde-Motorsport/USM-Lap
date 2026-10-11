"""
This module models the aerodynamics of a vehicle."""

from __future__ import annotations

from abc import ABC, abstractmethod
from math import pi
from typing import Annotated

from annotated_types import Unit
from pydantic import BaseModel, BeforeValidator, Field, PlainSerializer

from usmlap.core.filepath import LIBRARY_ROOT
from usmlap.core.library import Serialisable
from usmlap.core.registry import Registry


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
    roll_angle: float = Field(ge=-pi / 2, le=pi / 2, default=0)
    pitch_angle: float = Field(ge=-pi / 2, le=pi / 2, default=0)
    yaw_angle: float = Field(ge=-pi / 2, le=pi / 2, default=0)


class AeroModelInterface(ABC):
    """
    Abstract  base class for aero models.
    """

    @staticmethod
    @abstractmethod
    def get_lift_coefficient(
        package: AeroPackage, attitude: AeroAttitude
    ) -> float: ...

    @staticmethod
    @abstractmethod
    def get_drag_coefficient(
        package: AeroPackage, attitude: AeroAttitude
    ) -> float: ...


class ConstantAero(AeroModelInterface):
    """
    Constant aero model.

    Lift and drag coefficients do not change with velocity.

    Attributes:
        lift_coefficient (float): The lift coefficient (positive).
        drag_coefficient (float): The drag coefficient (positive).

    """

    @staticmethod
    def get_lift_coefficient(
        package: AeroPackage, attitude: AeroAttitude
    ) -> float:
        return package.lift_coefficient

    @staticmethod
    def get_drag_coefficient(
        package: AeroPackage, attitude: AeroAttitude
    ) -> float:
        return package.drag_coefficient


AeroModelRegistry = Registry[str, type[AeroModelInterface]]()
AeroModelRegistry.register("constant", ConstantAero)


class AeroPackage(
    Serialisable, library=LIBRARY_ROOT / "components" / "aero_packages"
):
    """
    The aerodynamic package of a vehicle.

    Attributes:
        frontal_area (float): The frontal area of the vehicle.
        aero_model (str): The aerodynamic model to use.

    """

    frontal_area: Annotated[float, Field(gt=0), Unit("m^2")]
    front_aero_distribution: Annotated[float, Field(ge=0, le=1), Unit("%")]
    centre_of_pressure_height: Annotated[float, Field(ge=0), Unit("m")]
    lift_coefficient: float = Field(gt=0)
    drag_coefficient: float = Field(gt=0)
    aero_model: Annotated[
        type[AeroModelInterface],
        BeforeValidator(AeroModelRegistry.get),
        PlainSerializer(AeroModelRegistry.get_key),
    ]

    def get_downforce(self, attitude: AeroAttitude) -> float:
        lift_coefficient = self.aero_model.get_lift_coefficient(self, attitude)
        return self.calculate_aero_force(lift_coefficient, attitude)

    def get_drag(self, attitude: AeroAttitude) -> float:
        drag_coefficient = self.aero_model.get_drag_coefficient(self, attitude)
        return self.calculate_aero_force(drag_coefficient, attitude)

    def calculate_aero_force(
        self,
        coefficient: float,
        attitude: AeroAttitude,
    ) -> float:
        return (
            0.5
            * coefficient
            * self.frontal_area
            * attitude.air_density
            * attitude.velocity**2
        )
