"""Fixtures for powertrain module unit tests."""

import math

import pytest

from usmlap.vehicle.powertrain import (
    Accumulator,
    Cell,
    Motor,
    MotorController,
    RWDPowertrain,
)
from usmlap.vehicle.powertrain.accumulator import CellVoltageLookup


@pytest.fixture
def cell() -> Cell:
    return Cell(
        print_name="Test Cell",
        capacity=40000,
        nominal_voltage=3.6,
        voltage_lookup=[
            CellVoltageLookup(state_of_charge=1, voltage=4.2),
            CellVoltageLookup(state_of_charge=0.5, voltage=3.5),
            CellVoltageLookup(state_of_charge=0, voltage=2.5),
        ],
        discharge_current=30,
        resistance=0.017,
        datasheet_url="test_url",
    )


@pytest.fixture
def accumulator(cell: Cell) -> Accumulator:
    return Accumulator(
        print_name="Test Accumulator",
        cell=cell,
        cells_in_parallel=5,
        cells_in_series=100,
    )


@pytest.fixture
def motor() -> Motor:
    return Motor(
        print_name="Test Motor",
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
    return MotorController(
        print_name="Test Motor Controller", resistance=0.2, efficiency=0.8
    )


@pytest.fixture
def powertrain(
    accumulator: Accumulator, motor: Motor, motor_controller: MotorController
) -> RWDPowertrain:
    return RWDPowertrain(
        accumulator=accumulator,
        motor=motor,
        motor_controller=motor_controller,
        soc_current_derate_point=0.3,
    )
