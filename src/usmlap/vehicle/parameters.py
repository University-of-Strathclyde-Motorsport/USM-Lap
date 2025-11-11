"""
This module contains code for getting and setting vehicle parameters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy

from .vehicle import Vehicle


class Parameter(ABC):
    """
    An abstract class representing a vehicle parameter.
    """

    _REGISTRY: dict[str, type[Parameter]] = {}
    name: str
    unit: str | None = None

    def __init_subclass__(
        cls: type[Parameter], parameter_name: str, unit: str | None = None
    ) -> None:
        super().__init_subclass__()
        cls._REGISTRY[parameter_name] = cls
        cls.name = parameter_name
        cls.unit = unit

    @classmethod
    def get_parameter(cls, parameter_name: str) -> Parameter:
        """
        Get a parameter from its name.

        Args:
            parameter_name (str): The name of the parameter.

        Raises:
            KeyError: If no parameter with the given name exists.

        Returns:
            parameter (type[Parameter]): A parameter object.
        """
        try:
            return cls._REGISTRY[parameter_name]()
        except KeyError:
            error_message = (
                f"Parameter '{parameter_name}' not found. "
                f"Available parameters: {list(cls._REGISTRY.keys())}"
            )
            raise KeyError(error_message)

    @classmethod
    def list_parameters(cls) -> list[str]:
        """
        Get a list of available parameters.

        Returns:
            parameters (list[str]): Available parameter names.
        """
        return list(cls._REGISTRY.keys())

    @classmethod
    def get_name_with_unit(cls) -> str:
        if cls.unit:
            return f"{cls.name} ({cls.unit})"
        else:
            return f"{cls.name} (-)"

    @staticmethod
    @abstractmethod
    def get_value(vehicle: Vehicle) -> float:
        """
        Get the value of a vehicle parameter.

        Args:
            vehicle (Vehicle): A vehicle object.

        Returns:
            value (float): The value of the corresponding parameter.
        """
        ...

    @staticmethod
    @abstractmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        """
        Set the value of a vehicle parameter.

        Args:
            vehicle (Vehicle): A vehicle object.
            value (float): The value to set the parameter to.

        Returns:
            vehicle (Vehicle): The modified vehicle object.
        """
        ...

    @classmethod
    def get_new_vehicle(
        cls, baseline_vehicle: Vehicle, value: float
    ) -> Vehicle:
        """
        Generate a new vehicle with a modified parameter value.

        Args:
            baseline_vehicle (Vehicle): The baseline vehicle to use.
            value (float): The updated parameter value.

        Returns:
            new_vehicle(Vehicle): A new vehicle with the updated parameter.
        """
        new_vehicle = deepcopy(baseline_vehicle)
        cls.set_value(new_vehicle, value)
        return new_vehicle


class CurbMass(Parameter, parameter_name="Curb Mass", unit="kg"):
    """The mass of the vehicle without the driver."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.inertia.curb_mass

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.inertia.curb_mass = value


class LiftCoefficient(Parameter, parameter_name="Lift Coefficient"):
    """The lift coefficient of the aero package."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.aero.aero_model.lift_coefficient

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.aero.aero_model.lift_coefficient = value


class DragCoefficient(Parameter, parameter_name="Drag Coefficient"):
    """The drag coefficient of the aero package."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.aero.aero_model.drag_coefficient

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.aero.aero_model.drag_coefficient = value


class FinalDriveRatio(Parameter, parameter_name="Final Drive Ratio"):
    """The final drive ratio of the transmission."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.transmission.final_drive_ratio

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.transmission.final_drive_ratio = value
