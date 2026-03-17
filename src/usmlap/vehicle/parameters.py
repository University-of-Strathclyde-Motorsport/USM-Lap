"""
This module contains code for getting and setting vehicle parameters.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import ClassVar, Optional

from .powertrain.accumulator import Cell
from .vehicle import Vehicle


class Parameter[T](ABC):
    """
    An abstract class representing a vehicle parameter.
    """

    _REGISTRY: ClassVar[dict[str, type[Parameter]]] = {}
    name: ClassVar[str]
    unit: ClassVar[Optional[str]] = None

    def __init_subclass__(
        cls: type[Parameter], name: str, unit: Optional[str] = None
    ) -> None:
        super().__init_subclass__()
        cls._REGISTRY[name] = cls
        cls.name = name
        cls.unit = unit

    @classmethod
    def get_parameter(cls, name: str) -> Parameter:
        """
        Get a parameter from its name.

        Args:
            name (str): The name of the parameter.

        Raises:
            KeyError: If no parameter with the given name exists.

        Returns:
            parameter (type[Parameter]): A parameter object.
        """
        try:
            return cls._REGISTRY[name]()
        except KeyError:
            error_message = (
                f"Parameter '{name}' not found. "
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
    def get_value(vehicle: Vehicle) -> T:
        """
        Get the value of a vehicle parameter.

        Args:
            vehicle (Vehicle): A vehicle object.

        Returns:
            value (T): The value of the corresponding parameter.
        """
        ...

    @staticmethod
    @abstractmethod
    def set_value(vehicle: Vehicle, value: T) -> None:
        """
        Set the value of a vehicle parameter.

        Args:
            vehicle (Vehicle): A vehicle object.
            value (T): The value to set the parameter to.

        Returns:
            vehicle (Vehicle): The modified vehicle object.
        """
        ...


def get_new_vehicle(
    baseline: Vehicle, parameter: type[Parameter], value: float
) -> Vehicle:
    """
    Generate a new vehicle with a modified parameter value.

    Args:
        baseline (Vehicle): The baseline vehicle to use.
        parameter (type[Parameter]): The parameter to modify.
        value (float): The updated parameter value.

    Returns:
        new_vehicle(Vehicle): A new vehicle with the updated parameter.
    """
    new_vehicle = deepcopy(baseline)
    parameter.set_value(new_vehicle, value)
    return new_vehicle


# Aerodynamics
class LiftCoefficient(Parameter[float], name="Lift Coefficient"):
    """The lift coefficient of the aero package."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.aero.aero_model.lift_coefficient

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.aero.aero_model.lift_coefficient = value


class DragCoefficient(Parameter[float], name="Drag Coefficient"):
    """The drag coefficient of the aero package."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.aero.aero_model.drag_coefficient

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.aero.aero_model.drag_coefficient = value


class FrontalArea(Parameter[float], name="Frontal Area", unit="m^2"):
    """The frontal area of the aerodynamic package."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.aero.frontal_area

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.aero.frontal_area = value


# Driver
class DriverMass(Parameter[float], name="Driver Mass", unit="kg"):
    """The mass of the driver."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.driver.mass

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.driver.mass = value


# Inertia
class CurbMass(Parameter[float], name="Curb Mass", unit="kg"):
    """The mass of the vehicle without the driver."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.inertia.curb_mass

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.inertia.curb_mass = value


class DrivetrainInertia(Parameter[float], name="Drivetrain Inertia", unit="kg"):
    """Equivalent mass of the drivetrain inertia, measured at the wheel."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.inertia.equivalent_drivetrain_inertia

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.inertia.equivalent_drivetrain_inertia = value


# Transmission
class FinalDriveRatio(Parameter[float], name="Final Drive Ratio"):
    """The final drive ratio of the transmission."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.transmission.final_drive_ratio

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.transmission.final_drive_ratio = value


# Accumulator


class AccumulatorCell(Parameter[Cell], name="Cell"):
    """The cell of the accumulator."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> Cell:
        return vehicle.powertrain.accumulator.cell

    @staticmethod
    def set_value(vehicle: Vehicle, value: Cell) -> None:
        vehicle.powertrain.accumulator.cell = value


class CellsInSeries(Parameter[int], name="Cells in Series"):
    """The number of cells in series in the accumulator."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> int:
        return vehicle.powertrain.accumulator.cells_in_series

    @staticmethod
    def set_value(vehicle: Vehicle, value: int) -> None:
        vehicle.powertrain.accumulator.cells_in_series = value


class CellsInParallel(Parameter[int], name="Cells in Parallel"):
    """The number of cells in parallel in the accumulator."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> int:
        return vehicle.powertrain.accumulator.cells_in_parallel

    @staticmethod
    def set_value(vehicle: Vehicle, value: int) -> None:
        vehicle.powertrain.accumulator.cells_in_parallel = value


# Powertrain
class DischargeCurrentLimit(Parameter[float], name="Discharge Current Limit"):
    """The discharge current limit of the powertrain."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.powertrain.discharge_current_limit

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.powertrain.discharge_current_limit = value
