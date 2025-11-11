import math

import pytest

from usmlap.vehicle.powertrain.accumulator import Accumulator, Cell
from usmlap.vehicle.powertrain.motor import Motor
from usmlap.vehicle.powertrain.motor_controller import MotorController
from usmlap.vehicle.powertrain.powertrain import RWDPowertrain


@pytest.fixture
def cell() -> Cell:
    return Cell(
        name="Test Cell",
        capacity=40000,
        nominal_voltage=3.6,
        charge_voltage=4.2,
        discharge_voltage=2.5,
        discharge_current=30,
        resistance=0.017,
        datasheet_url="test_url",
    )


@pytest.fixture
def accumulator(cell: Cell) -> Accumulator:
    return Accumulator(cell=cell, cells_in_parallel=5, cells_in_series=100)


@pytest.fixture
def motor() -> Motor:
    return Motor(
        name="Test Motor",
        electrical_resistance=0.2,
        peak_torque=250,
        continuous_torque=100,
        peak_current=300,
        continuous_current=150,
        maximum_rpm=15000 / math.pi,
        rated_voltage=600,
        datasheet_url="test_url",
    )


@pytest.fixture
def motor_controller() -> MotorController:
    return MotorController(name="Test Motor Controller", resistance=0.2)


@pytest.fixture
def powertrain(
    accumulator: Accumulator, motor: Motor, motor_controller: MotorController
) -> RWDPowertrain:
    return RWDPowertrain(
        accumulator=accumulator, motor=motor, motor_controller=motor_controller
    )
