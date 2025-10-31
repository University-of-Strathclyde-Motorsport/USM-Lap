import pytest
from usmlap.vehicle.powertrain.accumulator import Cell, Accumulator


def test_cell_voltage(cell: Cell) -> None:
    assert cell.get_voltage(state_of_charge=1) == pytest.approx(4.2)
    assert cell.get_voltage(state_of_charge=0) == pytest.approx(2.5)
    assert cell.get_voltage(state_of_charge=0.5) == pytest.approx(3.35)
    with pytest.raises(ValueError):
        cell.get_voltage(state_of_charge=2)
    with pytest.raises(ValueError):
        cell.get_voltage(state_of_charge=-1)


def test_cell_count(accumulator: Accumulator) -> None:
    assert accumulator.number_of_cells == 500


def test_accumulator_capacity(accumulator: Accumulator) -> None:
    assert accumulator.capacity == 20000000


def test_maximum_voltage(accumulator: Accumulator) -> None:
    assert accumulator.maximum_voltage == 420


def test_minimum_voltage(accumulator: Accumulator) -> None:
    assert accumulator.minimum_voltage == 250


def test_resistance(accumulator: Accumulator) -> None:
    assert accumulator.resistance == pytest.approx(0.34)


def test_maximum_discharge_current(accumulator: Accumulator) -> None:
    assert accumulator.maximum_discharge_current == 150


def test_accumulator_voltage(accumulator: Accumulator) -> None:
    assert accumulator.get_voltage(state_of_charge=1) == 420
    assert accumulator.get_voltage(state_of_charge=0) == 250
    assert accumulator.get_voltage(state_of_charge=0.5) == 335
    with pytest.raises(ValueError):
        accumulator.get_voltage(state_of_charge=2)
    with pytest.raises(ValueError):
        accumulator.get_voltage(state_of_charge=-1)
