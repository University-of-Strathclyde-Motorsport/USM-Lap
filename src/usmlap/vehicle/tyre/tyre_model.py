"""
This module contains various tyre model implementations.
"""

from abc import abstractmethod
from math import sqrt
from typing import Annotated, Literal

from annotated_types import Unit
from pydantic import Field, PositiveFloat
from pydantic.dataclasses import dataclass

from ..common import AbstractSubsystem, Component, Subsystem


@dataclass
class TyreAttitude(object):
    """
    Parameters describing the attitude of a tyre.

    Attributes:
        normal_load (float): The normal load acting on the tyre.
    """

    normal_load: Annotated[float, Field(ge=0), Unit("N")]


class TyreModelInterface(AbstractSubsystem):
    """
    Abstract base class for tyre models.
    """

    @abstractmethod
    def calculate_lateral_force(
        self, tyre_attitude: TyreAttitude, required_fx: float = 0
    ) -> float:
        """
        Calculates the lateral force available at the tyre.

        Args:
            tyre_attitude (TyreAttitude):
                The attitude of the tyre.
            required_fx (float, optional):
                The longitudinal force which must be maintained. Defaults to 0.

        Returns:
            fy (float): The lateral force available at the tyre.
        """
        pass

    @abstractmethod
    def calculate_longitudinal_force(
        self, tyre_attitude: TyreAttitude, required_fy: float = 0
    ) -> float:
        """
        Calculates the longitudinal force available at the tyre.

        Args:
            tyre_attitude (TyreAttitude):
                The attitude of the tyre.
            required_fy (float, optional):
                The lateral force which must be maintained. Defaults to 0.

        Returns:
            fx (float): The longitudinal force available at the tyre.
        """
        pass

    @abstractmethod
    def get_slip_ratio(self, tyre_attitude: TyreAttitude, fx: float) -> float:
        """
        Calculate the slip ratio required to generate longitudinal force.

        Args:
            tyre_attitude (TyreAttitude): The attitude of the tyre.
            fx (float): The longitudinal force required.

        Returns:
            slip_ratio (float):
                The slip ratio required to generate the longitudinal force.
        """
        pass

    @abstractmethod
    def get_slip_angle(self, tyre_attitude: TyreAttitude, fy: float) -> float:
        """
        Calculate the slip angle required to generate lateral force.

        Args:
            tyre_attitude (TyreAttitude): The attitude of the tyre.
            fy (float): The lateral force required.

        Returns:
            slip_angle (float):
                The slip angle required to generate the lateral force.
        """
        pass


class LinearTyreModel(TyreModelInterface, type="linear_tyre_model"):
    """
    Implements a load-sensitive linear tyre model.

    Attributes:
        mu_x_peak (float):
            The peak coefficient of longitudinal friction.
        mu_x_load_sensitivity (float):
            The sensitivity of longitudinal friction to load.
        mu_y_peak (float):
            The peak coefficient of lateral friction.
        mu_y_load_sensitivity (float):
            The sensitivity of lateral friction to load.
        slip_stiffness (float):
            The longitudinal force generated per unit of slip ratio.
        cornering_stiffness (float):
            The lateral force generated per unit of slip angle.
    """

    model_type: Literal["linear"]

    mu_x_peak: PositiveFloat
    mu_x_load_sensitivity: Annotated[float, Unit("1/N")]
    mu_y_peak: PositiveFloat
    mu_y_load_sensitivity: Annotated[float, Unit("1/N")]
    slip_stiffness: float
    cornering_stiffness: float

    def _get_mu_x(self, normal_load: float) -> float:
        return self.mu_x_peak - (self.mu_x_load_sensitivity * normal_load)

    def _get_mu_y(self, normal_load: float) -> float:
        return self.mu_y_peak - (self.mu_y_load_sensitivity * normal_load)

    def _get_fx_max(self, normal_load: float) -> float:
        return self._get_mu_x(normal_load) * normal_load

    def _get_fy_max(self, normal_load: float) -> float:
        return self._get_mu_y(normal_load) * normal_load

    @staticmethod
    def _get_scale_factor(required_force: float, maximum_force: float) -> float:
        if required_force > maximum_force:
            raise ValueError("Required force is greater than maximum")
        return sqrt(1 - (required_force / maximum_force) ** 2)

    def calculate_lateral_force(
        self, tyre_attitude: TyreAttitude, required_fx: float = 0
    ) -> float:
        fx_max = self._get_fx_max(tyre_attitude.normal_load)
        fy_max = self._get_fy_max(tyre_attitude.normal_load)
        return fy_max * self._get_scale_factor(required_fx, fx_max)

    def calculate_longitudinal_force(
        self, tyre_attitude: TyreAttitude, required_fy: float = 0
    ) -> float:
        fx_max = self._get_fx_max(tyre_attitude.normal_load)
        fy_max = self._get_fy_max(tyre_attitude.normal_load)
        return fx_max * self._get_scale_factor(required_fy, fy_max)

    def get_slip_ratio(self, tyre_attitude: TyreAttitude, fx: float) -> float:
        return fx / self.slip_stiffness

    def get_slip_angle(self, tyre_attitude: TyreAttitude, fy: float) -> float:
        return fy / self.cornering_stiffness


TyreModel = Annotated[LinearTyreModel, Field(discriminator="model_type")]


class Tyre(Component, library="tyres.json"):
    """
    A racing tyre.

    Attributes:
        unloaded_radius (float): The unloaded radius of the tyre.
        tyre_model (TyreModel): The tyre model.
    """

    unloaded_radius: float
    tyre_model: TyreModel


class Tyres(Subsystem):
    """
    The tyres of a vehicle.

    Attributes:
        front (TyreModel): The front tyres of the vehicle.
        rear (TyreModel): The rear tyres of the vehicle.
    """

    front: Tyre
    rear: Tyre
