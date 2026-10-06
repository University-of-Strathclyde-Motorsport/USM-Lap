"""
Fixtures for powertrain module unit tests."""

import math

import pytest

from usmlap.vehicle.powertrain.accumulator import (
    Accumulator,
    ThermalDerateCurve,
    _ThermalDerateNode,
)
from usmlap.vehicle.powertrain.cell import (
    Cell,
    CellState,
    StateOfCharge,
    _CellVoltageLookup,
    _SOCResistanceLookup,
    _TemperatureResistanceLookup,
)
from usmlap.vehicle.powertrain.motor import Motor
from usmlap.vehicle.powertrain.motor_controller import MotorController
from usmlap.vehicle.powertrain.powertrain import RWDPowertrain


@pytest.fixture
def cell() -> Cell:
    return Cell(
        print_name="Test Cell",
        capacity=40000,
        charge_capacity=10000,
        thermal_mass=50,
        nominal_voltage=3.6,
        voltage_lookup=[
            _CellVoltageLookup(state_of_charge=1, voltage=4.2),
            _CellVoltageLookup(state_of_charge=0.5, voltage=3.5),
            _CellVoltageLookup(state_of_charge=0, voltage=2.5),
        ],
        max_discharge_current=30,
        resistance_lookup=[
            _TemperatureResistanceLookup(
                temperature=25,
                lookup=[
                    _SOCResistanceLookup(state_of_charge=0, resistance=0.01),
                    _SOCResistanceLookup(state_of_charge=1, resistance=0.01),
                ],
            ),
        ],
        datasheet_url="test_url",
    )


@pytest.fixture
def accumulator(cell: Cell) -> Accumulator:
    return Accumulator(
        print_name="Test Accumulator",
        cell=cell,
        cells_in_parallel=5,
        cells_in_series=100,
        soc_derate_point=StateOfCharge(0.3),
        thermal_derate_curve=ThermalDerateCurve(
            nodes=[
                _ThermalDerateNode(temperature=0, current=1),
                _ThermalDerateNode(temperature=100, current=1),
            ],
        ),
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
        print_name="Test Motor Controller",
        resistance=0.2,
        efficiency=0.8,
    )


@pytest.fixture
def powertrain(
    accumulator: Accumulator,
    motor: Motor,
    motor_controller: MotorController,
) -> RWDPowertrain:
    return RWDPowertrain(
        accumulator=accumulator,
        motor=motor,
        motor_controller=motor_controller,
        cooling_coefficient=24,
    )


@pytest.fixture
def cell_state() -> CellState:
    return CellState(soc=StateOfCharge(0.5), temperature=25)
