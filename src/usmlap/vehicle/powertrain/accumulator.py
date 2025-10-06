"""
This module models the electric accumulator of a vehicle.
"""

from pydantic import BaseModel
from ..common import Component


class Cell(Component):
    """
    An electrochemical cell.

    Attributes:
        capacity (float): Capacity of the cell.
        nominal_voltage (float): Nominal voltage of the cell.
        charge_voltage (float): Maximum voltage of the fully charged cell.
        discharge_voltage (float): Minimum voltage of the fully discharged cell.
        discharge_current (float): Maximum continuous discharge current.
        resistance (float): Internal resistance of the cell.
            Note that this is an approximation, and will be updated later.
        datasheet_url (str): URL to the datasheet of the cell.
    """

    capacity: float
    nominal_voltage: float
    charge_voltage: float
    discharge_voltage: float
    discharge_current: float
    resistance: float
    datasheet_url: str

    @classmethod
    def library_name(cls) -> str:
        return "cells.json"


class Accumulator(BaseModel):
    """
    An electric accumulator.

    Attributes:
        cell (Cell): The cell used in the accumulator.
        cells_in_parallel (int): Number of cells in parallel.
        cells_in_series (int): Number of cells in series.
    """

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
        return self.cell.charge_voltage * self.cells_in_series

    @property
    def minimum_voltage(self) -> float:
        return self.cell.discharge_voltage * self.cells_in_series

    @property
    def maximum_discharge_current(self) -> float:
        return self.cell.discharge_current * self.cells_in_parallel

    @property
    def resistance(self) -> float:
        return (
            self.cell.resistance * self.cells_in_series / self.cells_in_parallel
        )

