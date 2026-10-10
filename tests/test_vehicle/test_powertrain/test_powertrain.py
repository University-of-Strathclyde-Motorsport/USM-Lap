"""
Unit tests for powertrain module."""

import pytest

from usmlap.vehicle.powertrain.cell import CellState, StateOfCharge
from usmlap.vehicle.powertrain.powertrain import RWDPowertrain


def test_voltage_drop(powertrain: RWDPowertrain, cell_state: CellState) -> None:
    assert powertrain.get_voltage_drop(cell_state, current=0) == 0
    assert powertrain.get_voltage_drop(cell_state, current=1) == pytest.approx(
        0.4,
    )


def test_get_motor_voltage(
    powertrain: RWDPowertrain,
    cell_state: CellState,
) -> None:
    assert (
        powertrain.get_motor_voltage(CellState(soc=StateOfCharge(1)), current=0)
        == 420
    )
    assert (
        powertrain.get_motor_voltage(
            CellState(soc=StateOfCharge(0.5)), current=0
        )
        == 335
    )
    assert (
        powertrain.get_motor_voltage(CellState(soc=StateOfCharge(0)), current=0)
        == 250
    )
    assert (
        powertrain.get_motor_voltage(
            CellState(soc=StateOfCharge(1)), current=100
        )
        == 360
    )
    assert (
        powertrain.get_motor_voltage(
            CellState(soc=StateOfCharge(0.5)), current=100
        )
        == 295
    )
    assert (
        powertrain.get_motor_voltage(
            CellState(soc=StateOfCharge(0)), current=100
        )
        == 190
    )


def test_get_knee_speed(
    powertrain: RWDPowertrain,
    cell_state: CellState,
) -> None:
    assert powertrain.get_knee_speed(cell_state, current=0) == 1675 / 6
    assert powertrain.get_knee_speed(cell_state, current=100) == 1475 / 6


def test_get_maximum_motor_speed(
    powertrain: RWDPowertrain,
    cell_state: CellState,
) -> None:
    assert powertrain.get_maximum_motor_speed(cell_state) == 1675 / 6
