"""
This module contains code for getting and setting vehicle parameters.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, ClassVar, Optional

from .powertrain.accumulator import Cell
from .vehicle import Vehicle


class Parameter[T](ABC):
    """
    An abstract class representing a vehicle parameter.
    """

    _REGISTRY: ClassVar[dict[str, type[Parameter[Any]]]] = {}
    name: ClassVar[str]
    unit: ClassVar[Optional[str]] = None
    uncertainty: ClassVar[float] = 0
    implemented: ClassVar[bool] = True

    def __init_subclass__(
        cls: type[Parameter[T]],
        name: str,
        unit: Optional[str] = None,
        uncertainty: float = 0,
        implemented: bool = True,
    ) -> None:
        super().__init_subclass__()
        cls._REGISTRY[name] = cls
        cls.name = name
        cls.unit = unit
        cls.uncertainty = uncertainty
        cls.implemented = implemented

    @classmethod
    def get_parameter(cls, name: str) -> type[Parameter[T]]:
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
            return cls._REGISTRY[name]
        except KeyError:
            error_message = (
                f"Parameter '{name}' not found. "
                f"Available parameters: {list(cls._REGISTRY.keys())}"
            )
            raise KeyError(error_message)

    @classmethod
    def list_all_parameters(cls) -> list[type[Parameter[T]]]:
        """
        Get a list of available parameters.

        Returns:
            parameters (list[type[Parameters]]): Available parameters.
        """
        return list(cls._REGISTRY.values())

    @classmethod
    def get_name_with_unit(cls) -> str:
        if cls.unit:
            return f"{cls.name} ({cls.unit})"
        else:
            return f"{cls.name} (-)"

    @classmethod
    def append_unit(cls, value: str) -> str:
        if cls.unit:
            return f"{value} {cls.unit}"
        else:
            return value

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

    def __str__(self) -> str:
        return f"Test({super().get_type()})"


def get_new_vehicle[T](
    baseline: Vehicle,
    parameter: type[Parameter[T]],
    value: T,
    label: Optional[str] = None,
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
    if label is None:
        label = str(uuid.uuid4())
    new_vehicle = deepcopy(baseline)
    new_vehicle.label = label
    parameter.set_value(new_vehicle, value)
    return new_vehicle


def list_all_parameters() -> list[type[Parameter[Any]]]:
    """
    Get a list of available parameters.

    Returns:
        parameters (list[type[Parameters]]): Available parameters.
    """
    return list(Parameter.list_all_parameters())


# Aerodynamics
class LiftCoefficient(
    Parameter[float], name="Lift Coefficient", uncertainty=0.2
):
    """The lift coefficient of the aero package."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.aero.aero_model.lift_coefficient

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.aero.aero_model.lift_coefficient = value


class DragCoefficient(
    Parameter[float], name="Drag Coefficient", uncertainty=0.1
):
    """The drag coefficient of the aero package."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.aero.aero_model.drag_coefficient

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.aero.aero_model.drag_coefficient = value


class FrontalArea(
    Parameter[float], name="Frontal Area", unit="m²", uncertainty=0.001
):
    """The frontal area of the aerodynamic package."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.aero.frontal_area

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.aero.frontal_area = value


# Driver
class DriverMass(
    Parameter[float], name="Driver Mass", unit="kg", uncertainty=5
):
    """The mass of the driver."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.driver.mass

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.driver.mass = value


# Inertia
class CurbMass(Parameter[float], name="Curb Mass", unit="kg", uncertainty=2):
    """The mass of the vehicle without the driver."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.inertia.curb_mass

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.inertia.curb_mass = value


class DrivetrainInertia(
    Parameter[float],
    name="Drivetrain Inertia",
    unit="kg",
    uncertainty=1,
    implemented=False,
):
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


# Cell
class ElectricalCell(Parameter[Cell], name="Electrical Cell"):
    """The cell used in the vehicle."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> Cell:
        return vehicle.powertrain.accumulator.cell

    @staticmethod
    def set_value(vehicle: Vehicle, value: Cell) -> None:
        vehicle.powertrain.accumulator.cell = value


class CellCapacity(
    Parameter[float], name="Cell Capacity", unit="J", uncertainty=2000
):
    """The capacity of the cell."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.powertrain.accumulator.cell.capacity

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.powertrain.accumulator.cell.capacity = value


class CellDischargeCurrent(
    Parameter[float], name="Cell Discharge Current", unit="A", uncertainty=3
):
    """The maximum discharge current of the cell."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.powertrain.accumulator.cell.max_discharge_current

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.powertrain.accumulator.cell.max_discharge_current = value


class CellResistanceOffset(
    Parameter[float], name="Cell Resistance", unit="Ω", uncertainty=0.005
):
    """The internal resistance of the cell."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.powertrain.accumulator.cell.resistance_offset

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.powertrain.accumulator.cell.resistance_offset = value


class CellVoltageOffset(
    Parameter[float], name="Cell Voltage Offset", unit="V", uncertainty=0.1
):
    """The voltage offset of the cell."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.powertrain.accumulator.cell.voltage_offset

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.powertrain.accumulator.cell.voltage_offset = value


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


# Motor
class MotorResistance(
    Parameter[float],
    name="Motor Resistance",
    unit="Ω",
    uncertainty=0.2,
    implemented=False,
):
    """Internal resistance of the motor."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.powertrain.motor.electrical_resistance

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.powertrain.motor.electrical_resistance = value


class PeakTorque(
    Parameter[float], name="Peak Torque", unit="Nm", uncertainty=10
):
    """Peak torque available from the motor."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.powertrain.motor.peak_torque

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.powertrain.motor.peak_torque = value


class MotorPeakCurrent(
    Parameter[float], name="Motor Peak Current", unit="A", uncertainty=10
):
    """Current required to deliver the peak torque."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.powertrain.motor.peak_current

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.powertrain.motor.peak_current = value


class MaximumRPM(
    Parameter[float], name="Maximum Motor RPM", unit="rpm", uncertainty=200
):
    """Maximum RPM of the motor."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.powertrain.motor.maximum_rpm

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.powertrain.motor.maximum_rpm = value


class MotorRatedVoltage(
    Parameter[float], name="Motor Rated Voltage", unit="V", uncertainty=10
):
    """Rated voltage of the motor."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.powertrain.motor.rated_voltage

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.powertrain.motor.rated_voltage = value


# Motor Controller
class MotorControllerResistance(
    Parameter[float],
    name="Motor Controller Resistance",
    unit="Ω",
    uncertainty=0.05,
):
    """The resistance of the motor controller."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.powertrain.motor_controller.resistance

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.powertrain.motor_controller.resistance = value


# Powertrain
class DischargeCurrentLimit(Parameter[float], name="Discharge Current Limit"):
    """The discharge current limit of the powertrain."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.powertrain.discharge_current_limit

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.powertrain.discharge_current_limit = value


# Tyre
class FrontTyreRadius(
    Parameter[float],
    name="Front Tyre Radius",
    unit="m",
    uncertainty=0.005,
    implemented=False,
):
    """The radius of the tyre."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.tyres.front.unloaded_radius

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.tyres.front.unloaded_radius = value


class RearTyreRadius(
    Parameter[float], name="Rear Tyre Radius", unit="m", uncertainty=0.005
):
    """The radius of the tyre."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.tyres.rear.unloaded_radius

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.tyres.rear.unloaded_radius = value


class FrontTyreLongGripPeak(
    Parameter[float], name="Front Tyre Peak Long. Grip", uncertainty=0.1
):
    """The peak longitudinal grip of the front tyre."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.tyres.front.tyre_model.mu_x_peak

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.tyres.front.tyre_model.mu_x_peak = value


class FrontTyreLongGripSens(
    Parameter[float],
    name="Front Tyre Long. Grip Load Sens.",
    unit="N⁻¹",
    uncertainty=0.0001,
):
    """The load sensitivity of the longitudinal grip of the front tyre."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.tyres.front.tyre_model.mu_x_load_sensitivity

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.tyres.front.tyre_model.mu_x_load_sensitivity = value


class FrontTyreLatGripPeak(
    Parameter[float], name="Front Tyre Peak Lat. Grip", uncertainty=0.1
):
    """The peak lateral grip of the front tyre."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.tyres.front.tyre_model.mu_y_peak

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.tyres.front.tyre_model.mu_y_peak = value


class FrontTyreLatGripSens(
    Parameter[float],
    name="Front Tyre Lat. Grip Load Sens.",
    unit="N⁻¹",
    uncertainty=0.0001,
):
    """The load sensitivity of the lateral grip of the front tyre."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.tyres.front.tyre_model.mu_y_load_sensitivity

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.tyres.front.tyre_model.mu_y_load_sensitivity = value


class RearTyreLongGripPeak(
    Parameter[float], name="Rear Tyre Peak Long. Grip", uncertainty=0.1
):
    """The peak longitudinal grip of the rear tyre."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.tyres.rear.tyre_model.mu_x_peak

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.tyres.rear.tyre_model.mu_x_peak = value


class RearTyreLongGripSens(
    Parameter[float],
    name="Rear Tyre Long. Grip Load Sens.",
    unit="N⁻¹",
    uncertainty=0.0001,
):
    """The load sensitivity of the longitudinal grip of the rear tyre."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.tyres.rear.tyre_model.mu_x_load_sensitivity

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.tyres.rear.tyre_model.mu_x_load_sensitivity = value


class RearTyreLatGripPeak(
    Parameter[float], name="Rear Tyre Peak Lat. Grip", uncertainty=0.1
):
    """The peak lateral grip of the rear tyre."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.tyres.rear.tyre_model.mu_y_peak

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.tyres.rear.tyre_model.mu_y_peak = value


class RearTyreLatGripSens(
    Parameter[float],
    name="Rear Tyre Lat. Grip Load Sens.",
    unit="N⁻¹",
    uncertainty=0.0001,
):
    """The load sensitivity of the lateral grip of the rear tyre."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.tyres.rear.tyre_model.mu_y_load_sensitivity

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.tyres.rear.tyre_model.mu_y_load_sensitivity = value


class CoolingCoefficient(
    Parameter[float], name="Cooling Coefficient", uncertainty=5
):
    """The cooling coefficient of the powertrain."""

    @staticmethod
    def get_value(vehicle: Vehicle) -> float:
        return vehicle.powertrain.cooling_coefficient

    @staticmethod
    def set_value(vehicle: Vehicle, value: float) -> None:
        vehicle.powertrain.cooling_coefficient = value
