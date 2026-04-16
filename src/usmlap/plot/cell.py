"""
This module contains code for plotting cell maps.
"""

import matplotlib.pyplot as plt
import numpy as np

from usmlap.plot.style import USM_BLUE
from usmlap.vehicle.powertrain import Cell

RESOLUTION = 1000
NOMINAL_TEMPERATURE = 25

AXIS_LABELS = {
    "soc": "State of Charge (%)",
    "voltage": "Voltage (V)",
    "resistance": "DC Impedance (mΩ)",
    "current": "Discharge Current (A)",
    "temperature": "Temperature (°C)",
}


def plot_cell_parameters(
    cell: Cell, derate_soc: float = 0.3, t_min: float = 0, t_max: float = 60
) -> None:
    """
    Plot the parameters of a cell.

    Args:
        cell (Cell): The cell to plot.
        derate_soc (float): The state of charge at which to begin derating current.
        t_min (float): The minimum temperature to plot.
        t_max (float): The maximum temperature to plot.
    """

    fig, axs = plt.subplots(2, 2)
    ((ax_voltage, ax_soc_derate), (ax_resistance, ax_thermal_derate)) = axs

    _plot_voltage(cell, ax_voltage)
    _plot_resistance(cell, ax_resistance)
    _plot_soc_derate(cell, ax_soc_derate, derate_soc)
    _plot_thermal_derate(cell, ax_thermal_derate)

    fig.suptitle(f"Cell Characteristics\n{cell.print_name}")

    plt.tight_layout()
    plt.show()


def _plot_voltage(cell: Cell, ax: plt.Axes) -> None:
    """Plot voltage against state of charge."""
    state_of_charge = np.linspace(0, 1, RESOLUTION)
    voltage = [cell.get_voltage(soc) for soc in state_of_charge]
    ax.plot(state_of_charge * 100, voltage, color=USM_BLUE)
    ax.set_xlabel(AXIS_LABELS["soc"])
    ax.set_ylabel(AXIS_LABELS["voltage"])
    ax.set_title("Voltage")
    ax.grid(True)
    ax.set_xlim(0, 100)


def _plot_resistance(cell: Cell, ax: plt.Axes) -> None:
    """Plot resistance against state of charge."""
    state_of_charge = np.linspace(0, 1, RESOLUTION)
    temperature = NOMINAL_TEMPERATURE
    resistance = [cell.resistance(temperature) * 1000 for _ in state_of_charge]
    ax.plot(state_of_charge * 100, resistance, color=USM_BLUE)
    ax.set_xlabel(AXIS_LABELS["soc"])
    ax.set_ylabel(AXIS_LABELS["resistance"])
    ax.set_title("Resistance")
    ax.grid(True)
    ax.set_xlim(0, 100)


def _plot_soc_derate(cell: Cell, ax: plt.Axes, derate_soc: float) -> None:
    """Plot current against state of charge."""
    state_of_charge = np.linspace(0, 1, RESOLUTION)
    current = [
        cell.discharge_current(soc, derate_soc) for soc in state_of_charge
    ]
    ax.plot(state_of_charge * 100, current, color=USM_BLUE)
    ax.set_xlabel(AXIS_LABELS["soc"])
    ax.set_ylabel(AXIS_LABELS["current"])
    ax.set_title("SOC Current Derating")
    ax.grid(True)
    ax.set_xlim(0, 100)


def _plot_thermal_derate(cell: Cell, ax: plt.Axes) -> None:
    """Plot current against temperature."""
    t_min = cell.minimum_temperature()
    t_max = cell.maximum_temperature()
    temperature = np.linspace(t_min, t_max, RESOLUTION)
    resistance = [cell.resistance(t) * 1000 for t in temperature]
    ax.plot(temperature, resistance, color=USM_BLUE)
    ax.set_xlabel(AXIS_LABELS["temperature"])
    ax.set_ylabel(AXIS_LABELS["resistance"])
    ax.set_title("Resistance vs Temperature")
    ax.grid(True)
    ax.set_xlim(t_min, t_max)
