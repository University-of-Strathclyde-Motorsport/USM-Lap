"""
This module models the electric accumulator of a vehicle.
"""

from ..common import Component, Subsystem


class Cell(Component, library="cells.json"):
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

        return (
            self.charge_voltage * state_of_charge
            + self.discharge_voltage * (1 - state_of_charge)
        )


class Accumulator(Subsystem):
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
