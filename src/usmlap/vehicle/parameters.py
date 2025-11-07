"""
This module contains code for getting and setting vehicle parameters.
"""

from abc import ABC, abstractmethod
from .vehicle import Vehicle
from copy import deepcopy


class Parameter(ABC):
    """
    An abstract class representing a vehicle parameter.
    """

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
            vehicle (Vehicle): The baseline vehicle to use.
            value (float): The updated parameter value.

        Returns:
            new_vehicle(Vehicle): A new vehicle with the updated parameter.
        """
        new_vehicle = deepcopy(baseline_vehicle)
        cls.set_value(new_vehicle, value)
        return new_vehicle


class CurbMass(Parameter):
    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.inertia.curb_mass

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.inertia.curb_mass = value


class LiftCoefficient(Parameter):
    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.aero.aero_model.lift_coefficient

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.aero.aero_model.lift_coefficient = value


class DragCoefficient(Parameter):
    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.aero.aero_model.drag_coefficient

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.aero.aero_model.drag_coefficient = value
