"""
This module models the electric accumulator of a vehicle.
"""

from dataclasses import dataclass
from functools import cached_property

import numpy as np

from usmlap.utils.library import LIBRARY_ROOT, HasLibrary

NOMINAL_TEMPERATURE = 25


@dataclass
class CellState(object):
    """The state of a cell in the accumulator."""

    state_of_charge: float
    temperature: float = NOMINAL_TEMPERATURE


@dataclass
class CellVoltageLookup(object):
    """Value from cell voltage lookup table."""

    state_of_charge: float
    voltage: float


@dataclass
class TemperatureResistanceLookup(object):
    """Value from current temperature lookup table."""

    temperature: float
    resistance: float


class Cell(HasLibrary, path=LIBRARY_ROOT / "components" / "cells"):
    """
    An electrochemical cell.

    Attributes:
        print_name (str): Printable name of the cell.
        capacity (float): Capacity of the cell.
        charge_capacity (float): Charge capacity of the cell.
        nominal_voltage (float): Nominal voltage of the cell.
        max_discharge_current (float): Maximum continuous discharge current.
        thermal_mass (float): Thermal mass of the cell.
        resistance (float): Internal resistance of the cell.
            Note that this is an approximation, and will be updated later.
        datasheet_url (str): URL to the datasheet of the cell.
        voltage_offset (float): Add or subtract a constant voltage
            to the cell voltage (default = 0).
        resistance_offset (float): Add or subtract a constant resistance
            to the cell resistance (default = 0).
    """

    print_name: str
    capacity: float
    charge_capacity: float
    nominal_voltage: float
    voltage_lookup: list[CellVoltageLookup]
    max_discharge_current: float
    resistance_lookup: list[TemperatureResistanceLookup]
    # resistance: float
    thermal_mass: float
    datasheet_url: str
    voltage_offset: float = 0
    resistance_offset: float = 0

    @cached_property
    def _soc_lookup_values(self) -> list[float]:
        self.voltage_lookup.sort(key=lambda node: node.state_of_charge)
        return [node.state_of_charge for node in self.voltage_lookup]

    @cached_property
    def _voltage_lookup_values(self) -> list[float]:
        self.voltage_lookup.sort(key=lambda node: node.state_of_charge)
        return [node.voltage for node in self.voltage_lookup]

    def get_voltage(self, state_of_charge: float) -> float:
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
    def _resistance_lookup_values(self) -> list[float]:
        self.resistance_lookup.sort(key=lambda node: node.temperature)
        return [node.resistance for node in self.resistance_lookup]

    @cached_property
    def _temperature_lookup_values(self) -> list[float]:
        self.resistance_lookup.sort(key=lambda node: node.temperature)
        return [node.temperature for node in self.resistance_lookup]

    def resistance(self, temperature: float) -> float:
        """Get the resistance of the cell at a given temperature."""
        resistance = np.interp(
            temperature,
            self._temperature_lookup_values,
            self._resistance_lookup_values,
        )
        return resistance + self.resistance_offset

    def minimum_temperature(self) -> float:
        return min(self._temperature_lookup_values)

    def maximum_temperature(self) -> float:
        return max(self._temperature_lookup_values)

    def discharge_current(
        self, state_of_charge: float, derate_soc: float
    ) -> float:
        """
        Get the available discharge current at a given state of charge.

        Above the derate SOC, the maximum discharge current is available.
        Below the derate SOC, the current is scaled linearly to zero.

        Args:
            state_of_charge (float): State of charge, between 0 and 1.
            derate_soc (float): State of charge at which to begin derating current.

        Returns:
            current (float): Available discharge current.
        """
        soc_derating = min(state_of_charge / derate_soc, 1)
        return self.max_discharge_current * soc_derating


class Accumulator(
    HasLibrary, path=LIBRARY_ROOT / "components" / "accumulators"
):
    """
    An electric accumulator.

    Attributes:
        print_name (str): Printable name of the accumulator.
        cell (Cell): The cell used in the accumulator.
        cells_in_parallel (int): Number of cells in parallel.
        cells_in_series (int): Number of cells in series.
    """

    print_name: str
    cell: Cell
    cells_in_parallel: int
    cells_in_series: int

    @property
    def number_of_cells(self) -> int:
        return self.cells_in_parallel * self.cells_in_series

    @property
    def capacity(self) -> float:
        return self.cell.capacity * self.number_of_cells

    @property
    def charge_capacity(self) -> float:
        return self.cell.charge_capacity * self.number_of_cells

    @property
    def thermal_mass(self) -> float:
        return self.cell.thermal_mass * self.number_of_cells

    @property
    def maximum_voltage(self) -> float:
        return self.get_voltage(state_of_charge=1)

    @property
    def minimum_voltage(self) -> float:
        return self.get_voltage(state_of_charge=0)

    def resistance(self, cell_state: CellState) -> float:
        cell_resistance = self.cell.resistance(cell_state.temperature)
        return cell_resistance * self.cells_in_series / self.cells_in_parallel

    def maximum_discharge_current(
        self, state_of_charge: float, derate_soc: float
    ) -> float:
        cell_current = self.cell.discharge_current(state_of_charge, derate_soc)
        return cell_current * self.cells_in_parallel

    def get_voltage(self, state_of_charge: float) -> float:
        """
        Get the voltage of the accumulator at a given state of charge.

        Args:
            state_of_charge (float): State of charge, between 0 and 1.

        Returns:
            voltage (float): Voltage of the accumulator.
        """
        return self.cell.get_voltage(state_of_charge) * self.cells_in_series

    def cell_current(self, current: float) -> float:
        return current / self.cells_in_parallel

    def heating_power(self, cell_state: CellState, current: float) -> float:
        resistance = self.resistance(cell_state)
        return current**2 * resistance
