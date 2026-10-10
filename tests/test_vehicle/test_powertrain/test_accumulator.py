"""
Unit tests for accumulator module."""

import pytest

from usmlap.vehicle.powertrain.accumulator import Accumulator
from usmlap.vehicle.powertrain.cell import Cell, CellState, StateOfCharge


def test_state_of_charge() -> None:
    assert StateOfCharge(1) == 1
    assert StateOfCharge(0) == 0
    assert StateOfCharge(0.5) == 0.5
    with pytest.raises(ValueError):
        StateOfCharge(2)
    with pytest.raises(ValueError):
        StateOfCharge(-1)


def test_cell_voltage(cell: Cell) -> None:
    assert cell.get_voltage(StateOfCharge(1)) == pytest.approx(4.2)
    assert cell.get_voltage(StateOfCharge(0)) == pytest.approx(2.5)
    assert cell.get_voltage(StateOfCharge(0.5)) == pytest.approx(3.35)


def test_cell_count(accumulator: Accumulator) -> None:
    assert accumulator.number_of_cells == 500


def test_accumulator_capacity(accumulator: Accumulator) -> None:
    assert accumulator.capacity == 20000000


def test_maximum_voltage(accumulator: Accumulator) -> None:
    assert accumulator.maximum_voltage == 420


def test_minimum_voltage(accumulator: Accumulator) -> None:
    assert accumulator.minimum_voltage == 250


def test_resistance(accumulator: Accumulator) -> None:
    cell_state = CellState(soc=StateOfCharge(0.5))
    assert accumulator.resistance(cell_state) == pytest.approx(0.2)


def test_maximum_discharge_current(accumulator: Accumulator) -> None:
    cell_state = CellState(soc=StateOfCharge(0.5))
    assert accumulator.maximum_discharge_current(cell_state) == 150


def test_accumulator_voltage(accumulator: Accumulator) -> None:
    assert accumulator.get_voltage(StateOfCharge(1)) == 420
    assert accumulator.get_voltage(StateOfCharge(0)) == 250
    assert accumulator.get_voltage(StateOfCharge(0.5)) == 335
