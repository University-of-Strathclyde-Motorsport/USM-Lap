"""
This module models the electric powertrain of a vehicle.
"""

from __future__ import annotations
from abc import ABC
from pydantic.dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt

from .accumulator import Accumulator
from .motor import Motor
from .motor_controller import MotorController


class Powertrain(ABC):
    """
    Abstract base class for powertrain models.
    """

    ...


@dataclass
class RWDPowertrain(Powertrain):
    """
    Implements a single motor, rear wheel drive electric powertrain.

    Attributes:
        accumulator (Accumulator): The accumulator storing energy.
        motor (Motor): The electric motor.
        motor_controller (MotorController): The motor controller.
    """

    accumulator: Accumulator
    motor: Motor
    motor_controller: MotorController

    def get_voltage_drop(self, current: float) -> float:
        """
        Calculate the voltage drop across the accumulator and motor controller.

        Args:
            current (float): Current drawn from the accumulator.

        Returns:
            voltage_drop (float): Voltage drop.
        """
        resistance = (
            self.accumulator.resistance + self.motor_controller.resistance
        )
        return current * resistance

    def get_motor_voltage(
        self, state_of_charge: float, current: float
    ) -> float:
        """
        Calculate the voltage applied to the motor.

        Args:
            state_of_charge (float): State of charge of the accumulator.
            current (float): Current drawn from the accumulator.

        Returns:
            motor_voltage (float): Voltage across the motor.
        """
        accumulator_voltage = self.accumulator.get_voltage(state_of_charge)
        voltage_drop = self.get_voltage_drop(current)
        return accumulator_voltage - voltage_drop

    def get_knee_speed(self, state_of_charge: float, current: float) -> float:
        """
        Calculate the knee speed of the motor.

        Args:
            state_of_charge (float): State of charge of the accumulator.
            current (float): Current drawn from the accumulator.

        Returns:
            knee_speed (float): Knee speed of the motor.
        """
        motor_voltage = self.get_motor_voltage(state_of_charge, current)
        knee_speed = self.motor.get_speed(motor_voltage)
        return knee_speed

    def get_maximum_motor_speed(self, state_of_charge: float) -> float:
        """
        Calculate the maximum speed of the motor.

        Args:
            state_of_charge (float): State of charge of the accumulator.

        Returns:
            maximum_speed (float): Maximum speed of the motor.
        """
        return self.get_knee_speed(state_of_charge, 0)

    def get_motor_torque(
        self, state_of_charge: float, current: float, motor_speed: float
    ) -> float:
        knee_speed = self.get_knee_speed(state_of_charge, current)
        maximum_torque = self.motor.get_torque(current)
        if motor_speed < knee_speed:
            torque = maximum_torque
        else:
            maximum_speed = self.get_maximum_motor_speed(state_of_charge)
            torque = (
                maximum_torque
                * (maximum_speed - motor_speed)
                / (maximum_speed - knee_speed)
            )
        return torque

    def plot_motor_curve(self, state_of_charge: float = 1) -> None:
        motor_curve = MotorCurveGenerator().generate(
            powertrain=self,
            state_of_charge=state_of_charge,
            current=self.accumulator.maximum_discharge_current,
        )
        motor_curve.plot()


@dataclass
class MotorCurveGenerator(object):
    """
    Generates a motor curve for a powertrain.

    Attributes:
        resolution (int): Number of points to generate.
    """

    resolution: int = 100

    def generate(
        self, powertrain: RWDPowertrain, state_of_charge: float, current: float
    ) -> MotorCurve:
        """
        Generate a motor curve for a powertrain.

        Args:
            powertrain (RWDPowertrain): Powertrain to generate the curve for.
            state_of_charge (float): State of charge of the accumulator.
            current (float): Current drawn from the accumulator.

        Returns:
            MotorCurve: The generated motor curve.
        """
        maximum_speed = powertrain.get_maximum_motor_speed(state_of_charge)
        motor_speeds = np.linspace(0, maximum_speed, self.resolution)
        motor_torques = np.zeros(self.resolution)
        for i in range(self.resolution):
            motor_torques[i] = powertrain.get_motor_torque(
                state_of_charge, current, motor_speeds[i]
            )
        motor_powers = motor_speeds * motor_torques

        return MotorCurve(
            speed=motor_speeds.tolist(),
            torque=motor_torques.tolist(),
            power=motor_powers.tolist(),
        )


@dataclass
class MotorCurve(object):
    """
    A curve of torque and power vs motor speed.

    Attributes:
        speed (list[float]): Motor speed in rad/s.
        torque (list[float]): Corresponding torque at each motor speed.
        power (list[float]): Corresponding power at each motor speed.
    """

    speed: list[float]
    torque: list[float]
    power: list[float]

    @property
    def rpm(self) -> list[float]:
        return [speed * (30 / np.pi) for speed in self.speed]

    @property
    def power_kw(self) -> list[float]:
        return [power / 1000 for power in self.power]

    def plot(self) -> None:
        """
        Plot the motor curve using matplotlib.

        Torque is plotted on the left axis in blue.
        Power is plotted on the right axis in green.
        """
        _, ax_torque = plt.subplots()
        ax_torque.plot(self.rpm, self.torque, color="blue")
        ax_torque.set_title("Motor Curves")
        ax_torque.set_xlabel("Motor Speed (RPM)")
        ax_torque.set_ylabel("Torque (Nm)")
        ax_torque.grid()

        ax_power = ax_torque.twinx()
        ax_power.plot(self.rpm, self.power_kw, color="green")
        ax_power.set_ylabel("Power (kW)")
        plt.show()
