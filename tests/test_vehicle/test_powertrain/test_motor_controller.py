"""Unit tests for motor controller module."""

import pytest

from usmlap.vehicle.powertrain.motor_controller import MotorController


@pytest.fixture
def motor_controller() -> MotorController:
    return MotorController(
        print_name="Test Motor Controller", resistance=0.2, efficiency=0.8
    )
