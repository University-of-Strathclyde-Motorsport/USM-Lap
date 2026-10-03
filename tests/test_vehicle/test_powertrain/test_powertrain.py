"""
Unit tests for powertrain module."""

import pytest

from usmlap.vehicle.powertrain import CellState, RWDPowertrain


def test_voltage_drop(powertrain: RWDPowertrain, cell_state: CellState) -> None:
    assert powertrain.get_voltage_drop(cell_state, current=0) == 0
    assert powertrain.get_voltage_drop(cell_state, current=1) == pytest.approx(
        0.54,
    )


def test_get_motor_voltage(
    powertrain: RWDPowertrain,
    cell_state: CellState,
) -> None:
    assert powertrain.get_motor_voltage(cell_state, current=0) == 420
    assert powertrain.get_motor_voltage(cell_state, current=0) == 335
    assert powertrain.get_motor_voltage(cell_state, current=0) == 250
    assert powertrain.get_motor_voltage(cell_state, current=100) == 366
    assert powertrain.get_motor_voltage(cell_state, current=100) == 281
    assert powertrain.get_motor_voltage(cell_state, current=100) == 196


def test_get_knee_speed(
    powertrain: RWDPowertrain,
    cell_state: CellState,
) -> None:
    assert powertrain.get_knee_speed(cell_state, current=0) == 350
    assert powertrain.get_knee_speed(cell_state, current=100) == 305
    assert powertrain.get_knee_speed(cell_state, current=0) == pytest.approx(
        625 / 3,
    )


def test_get_maximum_motor_speed(
    powertrain: RWDPowertrain,
    cell_state: CellState,
) -> None:
    assert powertrain.get_maximum_motor_speed(cell_state) == 350
    assert powertrain.get_maximum_motor_speed(cell_state) == pytest.approx(
        625 / 3,
    )
