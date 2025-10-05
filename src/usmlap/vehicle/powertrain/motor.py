"""
This module models the motor of a vehicle.
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from pydantic import BaseModel
from ..common import Component


class TorqueMap(BaseModel):
    """
    A torque map for a motor.

    Attributes:
        rpm (list[float]): Rotational speeds of the motor
        torque (list[float]): Corresponding torques at the motor shaft
    """

    rpm: list[float]
    torque: list[float]

    def lookup_torque(self, rpm: float) -> float:
        """
        Lookup the motor torque at a given speed.

        Args:
            rpm (float): Rotational speed of the motor.

        Returns:
            torque (float): Torque at the motor shaft.
        """
        return np.interp(rpm, self.rpm, self.torque)

    def plot(self) -> None:
        _, ax = plt.subplots()
        ax.plot(self.rpm, self.torque)
        ax.set_title("Torque Map")
        ax.set_xlabel("Speed (RPM)")
        ax.set_ylabel("Torque (Nm)")
        ax.grid()
        plt.show()


class Motor(Component):
    """
    An electric motor.

    Attributes:
        torque_map (TorqueMap): Torque map of the motor.
        max_rpm (float): Maximum rotational speed of the motor.
    """

    torque_map: TorqueMap
    max_rpm: float

    @classmethod
    def library_name(cls) -> str:
        return "motors.json"

    def get_torque(self, speed: float) -> float:
        """
        Get the torque output of the motor at a given speed.

        Args:
            speed (float): Rotational speed of the motor.

        Returns:
            torque (float): Torque at the motor shaft.
        """
        rpm = speed * (30 / math.pi)
        if rpm > self.max_rpm:
            torque = 0
        else:
            torque = self.torque_map.lookup_torque(rpm)
        return torque

    def get_power(self, speed: float) -> float:
        """
        Get the power output of the motor at a given speed.

        Args:
            speed (float): Rotational speed of the motor.

        Returns:
            power (float): Power output of the motor.
        """
        return speed * self.get_torque(speed)

    def plot_torque_curve(self) -> None:
        self.torque_map.plot()

    def plot_power_curve(self) -> None:
        _, ax = plt.subplots()
        rpm = np.linspace(0, self.max_rpm, 100)
        speed = rpm * (math.pi / 30)
        power = [self.get_power(s) / 1000 for s in speed]
        ax.plot(rpm, power)
        ax.set_title("Power Map")
        ax.set_xlabel("Speed (RPM)")
        ax.set_ylabel("Power (kW)")
        ax.grid()
        plt.show()
