"""
This module contains code for plotting cell maps.
"""

import matplotlib.pyplot as plt
import numpy as np

from usmlap.plot.style import COLOURMAP, USM_BLUE
from usmlap.vehicle.powertrain import Accumulator, Cell, CellState

RESOLUTION = 1000
NOMINAL_TEMPERATURE = 25
REFERENCE_TEMPERATURES = [25, 30, 35, 40, 45]
T_MIN = 0
T_MAX = 80

AXIS_LABELS = {
    "soc": "State of Charge (%)",
    "voltage": "Voltage (V)",
    "resistance": "DC Impedance (mΩ)",
    "current": "Discharge Current (A)",
    "temperature": "Temperature (°C)",
    "derate": "Available Current",
}


def plot_cell_parameters(accumulator: Accumulator) -> None:
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

    _plot_voltage(accumulator.cell, ax_voltage)
    _plot_resistance(accumulator.cell, ax_resistance)
    _plot_soc_derate(accumulator, ax_soc_derate)
    _plot_thermal_derate(accumulator, ax_thermal_derate)

    fig.suptitle(f"Cell Characteristics\n{accumulator.cell.print_name}")

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
    for temperature in REFERENCE_TEMPERATURES:
        resistances = []
        for soc in state_of_charge:
            cell_state = CellState(soc, temperature)
            resistances.append(cell.resistance(cell_state) * 1000)
        ax.plot(
            state_of_charge * 100,
            resistances,
            color=next(COLOURMAP),
            label=str(temperature),
        )
    ax.set_xlabel(AXIS_LABELS["soc"])
    ax.set_ylabel(AXIS_LABELS["resistance"])
    ax.set_title("Resistance")
    ax.grid(True)
    ax.legend(title="Temperature (°C)")
    ax.set_xlim(0, 100)


def _plot_soc_derate(accumulator: Accumulator, ax: plt.Axes) -> None:
    """Plot current against state of charge."""
    state_of_charge = np.linspace(0, 1, RESOLUTION)
    derate = [accumulator.soc_derate(soc) for soc in state_of_charge]
    ax.plot(state_of_charge * 100, derate, color=USM_BLUE)
    ax.set_xlabel(AXIS_LABELS["soc"])
    ax.set_ylabel(AXIS_LABELS["derate"])
    ax.set_title("SOC Current Derating")
    ax.grid(True)
    ax.set_xlim(0, 100)


def _plot_thermal_derate(accumulator: Accumulator, ax: plt.Axes) -> None:
    """Plot current against temperature."""
    temperature = np.linspace(T_MIN, T_MAX, RESOLUTION)
    derate = [accumulator.thermal_derate(t) for t in temperature]
    ax.plot(temperature, derate, color=USM_BLUE)
    ax.set_xlabel(AXIS_LABELS["temperature"])
    ax.set_ylabel(AXIS_LABELS["derate"])
    ax.set_title("Thermal Current Derating")
    ax.grid(True)
    ax.set_xlim(T_MIN, T_MAX)
