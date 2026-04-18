"""
This module models the electric accumulator of a vehicle.
"""

from dataclasses import dataclass
from functools import cached_property
from typing import Annotated

import numpy as np
from pydantic import BeforeValidator

from usmlap.utils.library import LIBRARY_ROOT, HasLibrary

from .cell import Cell, CellState, StateOfCharge

NOMINAL_TEMPERATURE = 25


@dataclass
class _ThermalDerateNode(object):
    """Node of a thermal derating curve."""

    temperature: float
    current: float


class ThermalDerateCurve(
    HasLibrary, path=LIBRARY_ROOT / "bms" / "thermal_derate"
):
    """
    Curve describing the thermal derating of the accumulator.
    """

    nodes: list[_ThermalDerateNode]

    @cached_property
    def _temperature(self) -> list[float]:
        self.nodes.sort(key=lambda node: node.temperature)
        return [node.temperature for node in self.nodes]

    @cached_property
    def _current(self) -> list[float]:
        self.nodes.sort(key=lambda node: node.temperature)
        return [node.current for node in self.nodes]

    def derate(self, temperature: float) -> float:
        return np.interp(temperature, self._temperature, self._current)


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
    soc_derate_point: Annotated[StateOfCharge, BeforeValidator(StateOfCharge)]
    thermal_derate_curve: ThermalDerateCurve

    @property
    def number_of_cells(self) -> int:
        return self.cells_in_parallel * self.cells_in_series

    @property
    def capacity(self) -> float:
        return self.cell.capacity * self.number_of_cells

    @property
    def charge_capacity(self) -> float:
        return self.cell.charge_capacity * self.cells_in_parallel

    @property
    def thermal_mass(self) -> float:
        return self.cell.thermal_mass * self.number_of_cells

    @property
    def maximum_voltage(self) -> float:
        return self.get_voltage(state_of_charge=StateOfCharge(1))

    @property
    def minimum_voltage(self) -> float:
        return self.get_voltage(state_of_charge=StateOfCharge(0))

    def resistance(self, cell_state: CellState) -> float:
        cell_resistance = self.cell.resistance(cell_state)
        return cell_resistance * self.cells_in_series / self.cells_in_parallel

    def soc_derate(self, state_of_charge: StateOfCharge) -> float:
        return min(state_of_charge / self.soc_derate_point, 1)

    def thermal_derate(self, temperature: float) -> float:
        return self.thermal_derate_curve.derate(temperature)

    def derate(self, cell_state: CellState) -> float:
        soc_derate = self.soc_derate(cell_state.soc)
        thermal_derate = self.thermal_derate(cell_state.temperature)
        return min(soc_derate, thermal_derate)

    def maximum_discharge_current(self, cell_state: CellState) -> float:
        cell_current = self.cell.discharge_current(cell_state)
        derate = self.derate(cell_state)
        return cell_current * self.cells_in_parallel * derate

    def get_voltage(self, state_of_charge: StateOfCharge) -> float:
        """Get the voltage of the accumulator at a given state of charge."""
        return self.cell.get_voltage(state_of_charge) * self.cells_in_series

    def heating_power(self, cell_state: CellState, current: float) -> float:
        resistance = self.resistance(cell_state)
        return current**2 * resistance
