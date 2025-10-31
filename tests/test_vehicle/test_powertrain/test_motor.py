import pytest
from usmlap.vehicle.powertrain.motor import Motor


def test_maximum_speed(motor: Motor) -> None:
    assert motor.maximum_speed == 500


def test_speed_per_volt(motor: Motor) -> None:
    assert motor.speed_per_volt == pytest.approx(5 / 6)


def test_torque_per_amp(motor: Motor) -> None:
    assert motor.torque_per_amp == pytest.approx(5 / 6)


def test_get_speed(motor: Motor) -> None:
    assert motor.get_speed(600) == 500


def test_get_torque(motor: Motor) -> None:
    assert motor.get_torque(30) == 25
