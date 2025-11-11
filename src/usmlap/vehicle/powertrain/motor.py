"""
This module models the motor of a vehicle.
"""

import math

from ..common import Component


class Motor(Component):
    """
    An electric motor.

    Attributes:
        electrical_resistance (float): Electrical resistance of the motor.
        peak_torque (float):
            Peak torque which the motor can deliver for a short period.
        continuous_torque (float):
            Maximum torque which the motor can deliver continuously.
        peak_current (float): Current required to deliver the peak torque.
        continuous_current (float):
            Current required to deliver the continuous torque.
        maximum_rpm (float): Maximum rotational speed of the motor.
        rated_voltage (float): Rated voltage of the motor.
        datasheet_url (str): URL for the datasheet of the motor.
    """

    electrical_resistance: float
    peak_torque: float
    continuous_torque: float
    peak_current: float
    continuous_current: float
    maximum_rpm: float
    rated_voltage: float
    datasheet_url: str

    @classmethod
    def library_name(cls) -> str:
        return "motors.json"

    @property
    def maximum_speed(self) -> float:
        return rpm_to_rads(self.maximum_rpm)

    @property
    def speed_per_volt(self) -> float:
        return self.maximum_speed / self.rated_voltage

    @property
    def torque_per_amp(self) -> float:
        return self.peak_torque / self.peak_current

    def get_speed(self, voltage: float) -> float:
        """
        Calculate the motor speed for an input voltage.

        Args:
            voltage (float): Voltage applied to the motor.

        Returns:
            speed (float): Rotational speed of the motor.
        """
        return voltage * self.speed_per_volt

    def get_torque(self, current: float) -> float:
        """
        Calculate the motor torque for an input current.

        Args:
            current (float): Current applied to the motor.

        Returns:
            torque (float): Torque output of the motor.
        """
        return current * self.torque_per_amp


def rpm_to_rads(rpm: float) -> float:
    """
    Convert from RPM to radians per second

    Args:
        rpm (float): Speed in revolutions per minute

    Returns:
        speed (float): Speed in radians per second
    """
    return rpm * (math.pi / 30)


def rads_to_rpm(speed: float) -> float:
    """
    Convert from radians per second to RPM

    Args:
        speed (float): Speed in radians per second

    Returns:
        rpm (float): Speed in revolutions per minute
    """
    return speed * (30 / math.pi)
