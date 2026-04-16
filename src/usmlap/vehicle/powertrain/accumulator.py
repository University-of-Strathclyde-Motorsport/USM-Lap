"""
This module models the electric accumulator of a vehicle.
"""

from dataclasses import dataclass
from functools import cached_property

import numpy as np

from usmlap.utils.library import LIBRARY_ROOT, HasLibrary


@dataclass
class CellVoltageLookup(object):
    """Value from cell voltage lookup table."""

    state_of_charge: float
    voltage: float


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
    nominal_voltage: float
    voltage_lookup: list[CellVoltageLookup]
    discharge_current: float
    resistance: float
    datasheet_url: str
    voltage_offset: float = 0

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
    def maximum_voltage(self) -> float:
        return self.get_voltage(state_of_charge=1)

    @property
    def minimum_voltage(self) -> float:
        return self.get_voltage(state_of_charge=0)

    @property
    def maximum_discharge_current(self) -> float:
        return self.cell.discharge_current * self.cells_in_parallel

    @property
    def resistance(self) -> float:
        return (
            self.cell.resistance * self.cells_in_series / self.cells_in_parallel
        )

    def get_voltage(self, state_of_charge: float) -> float:
        """
        Get the voltage of the accumulator at a given state of charge.

        Args:
            state_of_charge (float): State of charge, between 0 and 1.

        Returns:
            voltage (float): Voltage of the accumulator.
        """
        return self.cell.get_voltage(state_of_charge) * self.cells_in_series
