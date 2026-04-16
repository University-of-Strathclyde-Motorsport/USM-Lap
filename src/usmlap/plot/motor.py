"""
This module contains code for plotting motor performance curves.
"""

import math
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np

from usmlap.vehicle.powertrain import CellState, RWDPowertrain

from .style import COLOURMAP


def plot_motor_curve(
    powertrain: RWDPowertrain,
    state_of_charge: list[float] = [1, 0.8, 0.6, 0.4, 0.2],
    resolution: int = 1000,
) -> None:
    """
    Plot torque and power curves for a motor.

    Args:
        powertrain (RWDPowertrain): Powertrain to plot the curve for.
        state_of_charge (list[float], optional): List of state of charge values to plot.
            Defaults to [1, 0.8, 0.6, 0.4, 0.2].
        resolution (int, optional): Number of points to generate. Defaults to 1000.
    """
    fig, (ax_torque, ax_power) = plt.subplots(nrows=2, sharex=True)

    for soc in state_of_charge:
        cell_state = CellState(state_of_charge=soc, temperature=25)
        motor_curve = _generate_motor_curve(powertrain, cell_state, resolution)
        rpm = [rads_to_rpm(node.speed) for node in motor_curve]
        torque = [node.torque for node in motor_curve]
        power = [node.power / 1000 for node in motor_curve]

        label = f"SOC: {(soc * 100):.0f}%"
        colour = next(COLOURMAP)

        ax_torque.plot(rpm, torque, label=label, color=colour)
        ax_power.plot(rpm, power, label=label, color=colour)

    ax_torque.set_ylabel("Torque (Nm)")
    ax_power.set_ylabel("Power (kW)")
    ax_power.set_xlabel("Motor Speed (rpm)")
    fig.suptitle(f"Motor Curve\n{powertrain.motor.print_name}")

    for ax in [ax_torque, ax_power]:
        xlim = ax.get_xlim()
        ax.set_xlim(0, xlim[1])
        ax.legend(loc="best")
        ax.grid(True)

    plt.tight_layout()
    plt.show()


@dataclass
class _MotorCurveNode(object):
    """
    A node of a motor performance curve.

    Attributes:
        speed (float): Motor speed in rad/s.
        torque (float): Motor torque in Nm.
        power (float): Motor power in W.
    """

    speed: float
    torque: float

    @property
    def power(self) -> float:
        return self.speed * self.torque


def _generate_motor_curve(
    powertrain: RWDPowertrain, cell_state: CellState, resolution: int
) -> list[_MotorCurveNode]:
    """
    Generate a motor curve for a powertrain.
    """

    maximum_speed = powertrain.get_maximum_motor_speed(cell_state)
    speeds = np.linspace(0, maximum_speed, resolution).tolist()
    torques = [
        powertrain.get_motor_torque(cell_state, speed) for speed in speeds
    ]
    return [_MotorCurveNode(speed=s, torque=t) for s, t in zip(speeds, torques)]


def rads_to_rpm(speed: float) -> float:
    """Convert a speed from rad/s to rpm"""
    return speed * (30 / math.pi)
