"""
This module models electrical cells.
"""

from dataclasses import dataclass
from functools import cached_property
from typing import Any, Self

import numpy as np
from scipy.interpolate import interpn

from usmlap.utils.library import LIBRARY_ROOT, HasLibrary

NOMINAL_TEMPERATURE = 25

type Grid = np.ndarray[tuple[int, int], np.dtype[np.float64]]


class StateOfCharge(float):
    """
    State of charge of a cell.
    Must be a number between 0 and 1.
    """

    def __new__(cls, value: Any) -> Self:
        value = float(value)
        if value < 0 or value > 1:
            raise ValueError("State of charge must be between 0 and 1")
        return super().__new__(cls, value)

    def __str__(self) -> str:
        return f"{float(self) * 100:.3f}%"


@dataclass
class CellState(object):
    """
    The state of a cell in the accumulator.

    Attributes:
        soc (StateOfCharge): State of charge of the cell.
        temperature (float): Temperature of the cell.
    """

    soc: StateOfCharge
    temperature: float = NOMINAL_TEMPERATURE


@dataclass
class _CellVoltageLookup(object):
    """Value from cell voltage lookup table."""

    state_of_charge: float
    voltage: float


@dataclass
class _SOCResistanceLookup(object):
    """Value from SOC - resistance lookup table."""

    state_of_charge: float
    resistance: float


@dataclass
class _TemperatureResistanceLookup(object):
    """Row from temperature - resistance lookup table."""

    temperature: float
    lookup: list[_SOCResistanceLookup]


class Cell(HasLibrary, path=LIBRARY_ROOT / "components" / "cells"):
    """
    An electrochemical cell.

    Attributes:
        print_name (str): Printable name of the cell.
        capacity (float): Capacity of the cell.
        nominal_voltage (float): Nominal voltage of the cell.
        discharge_current (float): Maximum continuous discharge current.
        resistance (float): Internal resistance of the cell.
            Note that this is an approximation, and will be updated later.
        datasheet_url (str): URL to the datasheet of the cell.
        voltage_offset (float): Add or subtract a constant voltage
            to the cell voltage (default = 0).
    """

    print_name: str
    capacity: float
    charge_capacity: float
    thermal_mass: float
    nominal_voltage: float
    voltage_lookup: list[_CellVoltageLookup]
    max_discharge_current: float
    resistance_lookup: list[_TemperatureResistanceLookup]
    datasheet_url: str
    voltage_offset: float = 0
    resistance_offset: float = 0

    def __str__(self) -> str:
        return self.print_name

    @cached_property
    def _soc_lookup_values(self) -> list[float]:
        self.voltage_lookup.sort(key=lambda node: node.state_of_charge)
        return [node.state_of_charge for node in self.voltage_lookup]

    @cached_property
    def _voltage_lookup_values(self) -> list[float]:
        self.voltage_lookup.sort(key=lambda node: node.state_of_charge)
        return [node.voltage for node in self.voltage_lookup]

    def get_voltage(self, state_of_charge: StateOfCharge) -> float:
        """
        Get approximate cell voltage from state of charge.

        This function interpolates linearly
        between the charge and discharge voltage.

        Args:
            state_of_charge (float): State of charge, between 0 and 1.

        Returns:
            voltage (float): Voltage of the cell.
        """
        if state_of_charge < 0 or state_of_charge > 1:
            raise ValueError("State of charge must be between 0 and 1.")

        voltage = np.interp(
            state_of_charge,
            self._soc_lookup_values,
            self._voltage_lookup_values,
        )
        return voltage + self.voltage_offset

    @cached_property
    def _resistance_lookup(self) -> tuple[tuple[Grid, Grid], Grid]:
        self.resistance_lookup.sort(key=lambda node: node.temperature)
        soc = np.linspace(0, 1, 20)

        resistance_grid = []
        temperature = np.array(
            [node.temperature for node in self.resistance_lookup]
        )

        for i, temperature_lookup in enumerate(self.resistance_lookup):
            lookup = temperature_lookup.lookup
            lookup.sort(key=lambda node: node.state_of_charge)
            ref_soc = np.array([node.state_of_charge for node in lookup])
            ref_resistance = np.array([node.resistance for node in lookup])
            resistance = np.interp(soc, ref_soc, ref_resistance)

            if i == 0:
                resistance_grid = resistance
                continue

            resistance_grid = np.vstack((resistance_grid, resistance))

        return (soc, temperature), np.transpose(resistance_grid)

    @cached_property
    def _min_temp(self) -> float:
        return min([node.temperature for node in self.resistance_lookup])

    @cached_property
    def _max_temp(self) -> float:
        return max([node.temperature for node in self.resistance_lookup])

    def resistance(self, cell_state: CellState) -> float:
        """Get the resistance of the cell for a given cell state."""
        soc = cell_state.soc
        temp = min(max(cell_state.temperature, self._min_temp), self._max_temp)
        input_grid, resistance_grid = self._resistance_lookup
        resistance = float(
            interpn(input_grid, resistance_grid, (soc, temp), method="linear")
        )
        return resistance + self.resistance_offset

    def discharge_current(self, cell_state: CellState) -> float:
        """Get the available  discharge current for a given cell state.."""
        return self.max_discharge_current
