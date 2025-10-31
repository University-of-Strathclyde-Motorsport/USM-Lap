import pytest
from usmlap.vehicle.powertrain.powertrain import RWDPowertrain


def test_voltage_drop(powertrain: RWDPowertrain) -> None:
    assert powertrain.get_voltage_drop(current=0) == 0
    assert powertrain.get_voltage_drop(current=1) == pytest.approx(0.54)


def test_get_motor_voltage(powertrain: RWDPowertrain) -> None:
    assert powertrain.get_motor_voltage(state_of_charge=1, current=0) == 420
    assert powertrain.get_motor_voltage(state_of_charge=0.5, current=0) == 335
    assert powertrain.get_motor_voltage(state_of_charge=0, current=0) == 250
    assert powertrain.get_motor_voltage(state_of_charge=1, current=100) == 366
    assert powertrain.get_motor_voltage(state_of_charge=0.5, current=100) == 281
    assert powertrain.get_motor_voltage(state_of_charge=0, current=100) == 196


def test_get_knee_speed(powertrain: RWDPowertrain) -> None:
    assert powertrain.get_knee_speed(state_of_charge=1, current=0) == 350
    assert powertrain.get_knee_speed(state_of_charge=1, current=100) == 305
    assert powertrain.get_knee_speed(
        state_of_charge=0, current=0
    ) == pytest.approx(625 / 3)


def test_get_maximum_motor_speed(powertrain: RWDPowertrain) -> None:
    assert powertrain.get_maximum_motor_speed(state_of_charge=1) == 350
    assert powertrain.get_maximum_motor_speed(
        state_of_charge=0
    ) == pytest.approx(625 / 3)
