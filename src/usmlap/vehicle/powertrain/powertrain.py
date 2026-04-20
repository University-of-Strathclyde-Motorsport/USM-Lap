"""
This module models the electric powertrain of a vehicle.
"""

from __future__ import annotations

from abc import ABC
from typing import Optional

from pydantic import BaseModel

from .accumulator import Accumulator, CellState
from .motor import Motor
from .motor_controller import MotorController

COOLING_TEMPERATURE_THRESHOLD = 45


class PowertrainInterface(ABC, BaseModel):
    """
    Abstract base class for powertrain models.
    """

    # TODO: Why is BaseModel inheritance required?

    ...


class RWDPowertrain(PowertrainInterface):
    """
    Implements a single motor, rear wheel drive electric powertrain.

    Attributes:
        accumulator (Accumulator): The accumulator storing energy.
        motor (Motor): The electric motor.
        motor_controller (MotorController): The motor controller.
        soc_current_derate_point (float):
            State of charge at which to begin derating current.
        discharge_current_limit (float): Scaling factor for the current limit.
    """

    accumulator: Accumulator
    motor: Motor
    motor_controller: MotorController
    cooling_coefficient: float
    discharge_current_limit: float = 1

    def get_discharge_current(self, cell_state: CellState) -> float:
        """
        Get the available discharge current at a given state of charge.

        Above the derate point, the maximum discharge current is available.
        Below the derate point, the current is scaled linearly to zero.

        Args:
            state_of_charge (float): State of charge, between 0 and 1.

        Returns:
            current (float): Available discharge current.
        """
        maximum_discharge_current = self.accumulator.maximum_discharge_current(
            cell_state
        )
        return maximum_discharge_current * self.discharge_current_limit

    def get_voltage_drop(self, cell_state: CellState, current: float) -> float:
        """
        Calculate the voltage drop across the accumulator and motor controller.

        Args:
            current (float): Current drawn from the accumulator.

        Returns:
            voltage_drop (float): Voltage drop.
        """
        resistance = (
            self.accumulator.resistance(cell_state)
            + self.motor_controller.resistance
        )
        return current * resistance

    def get_motor_voltage(self, cell_state: CellState, current: float) -> float:
        """
        Calculate the voltage applied to the motor.

        Args:
            state_of_charge (float): State of charge of the accumulator.
            current (float): Current drawn from the accumulator.

        Returns:
            motor_voltage (float): Voltage across the motor.
        """
        accumulator_voltage = self.accumulator.get_voltage(cell_state.soc)
        voltage_drop = self.get_voltage_drop(cell_state, current)
        return accumulator_voltage - voltage_drop

    def get_knee_speed(
        self, cell_state: CellState, current: Optional[float] = None
    ) -> float:
        """
        Calculate the knee speed of the motor.

        Args:
            state_of_charge (float): State of charge of the accumulator.
            current (Optional[float]): Current drawn from the accumulator.
                If not provided, the maximum discharge current is used.

        Returns:
            knee_speed (float): Knee speed of the motor.
        """
        if current is None:
            current = self.get_discharge_current(cell_state)

        motor_voltage = self.get_motor_voltage(cell_state, current)
        knee_speed = self.motor.get_speed(motor_voltage)
        return knee_speed

    def get_maximum_motor_speed(self, cell_state: CellState) -> float:
        """
        Calculate the maximum speed of the motor.

        Args:
            state_of_charge (float): State of charge of the accumulator.

        Returns:
            maximum_speed (float): Maximum speed of the motor.
        """
        return self.get_knee_speed(cell_state, current=0)

    def get_motor_torque(
        self, cell_state: CellState, motor_speed: float
    ) -> float:
        discharge_current = self.get_discharge_current(cell_state)
        knee_speed = self.get_knee_speed(cell_state, discharge_current)
        maximum_speed = self.get_knee_speed(cell_state, current=0)
        maximum_torque = self.motor.get_torque(discharge_current)

        if motor_speed <= knee_speed:
            ratio = 1
        elif motor_speed >= maximum_speed:
            ratio = 0
        else:
            ratio = (maximum_speed - motor_speed) / (maximum_speed - knee_speed)

        return maximum_torque * ratio

    def get_motor_power(
        self, cell_state: CellState, motor_speed: float
    ) -> float:
        torque = self.get_motor_torque(cell_state, motor_speed)
        power = motor_speed * torque
        return power

    def get_powertrain_efficiency(self) -> float:
        return 0.8  # TODO: efficiency calculation

    def motor_to_accumulator_power(self, motor_power: float) -> float:
        return motor_power / self.get_powertrain_efficiency()

    def cooling_rate(
        self, cell_temperature: float, ambient_temperature: float
    ) -> float:
        if cell_temperature < COOLING_TEMPERATURE_THRESHOLD:
            return 0
        temperature_delta = cell_temperature - ambient_temperature
        return self.cooling_coefficient * max(temperature_delta, 0)
