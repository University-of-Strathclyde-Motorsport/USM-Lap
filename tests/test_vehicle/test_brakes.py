import pytest
import math
from usmlap.vehicle.brakes import (
    MasterCylinder,
    BrakeCaliper,
    BrakeDisc,
    BrakePad,
    BrakeLine,
    Brakes,
)


@pytest.fixture
def master_cylinder() -> MasterCylinder:
    return MasterCylinder(name="Cylinder", piston_diameter=0.2, colour="red")


@pytest.fixture
def brake_caliper() -> BrakeCaliper:
    return BrakeCaliper(name="Caliper", piston_count=2, piston_diameter=0.1)


@pytest.fixture
def brake_disc() -> BrakeDisc:
    return BrakeDisc(name="Disc", outer_diameter=0.3)


@pytest.fixture
def brake_pad() -> BrakePad:
    return BrakePad(name="Pad", height=0.02, coefficient_of_friction=0.5)


@pytest.fixture
def brake_line(
    master_cylinder: MasterCylinder,
    brake_caliper: BrakeCaliper,
    brake_disc: BrakeDisc,
    brake_pad: BrakePad,
) -> BrakeLine:
    return BrakeLine(
        cylinder=master_cylinder,
        caliper=brake_caliper,
        disc=brake_disc,
        pad=brake_pad,
    )


def test_master_cylinder_area(master_cylinder: MasterCylinder) -> None:
    assert master_cylinder.piston_area == pytest.approx(0.01 * math.pi)


def test_brake_caliper_area(brake_caliper: BrakeCaliper) -> None:
    assert brake_caliper.piston_area == pytest.approx(0.005 * math.pi)


def test_brake_line_area_scaling_factor(brake_line: BrakeLine) -> None:
    assert brake_line.area_scaling_factor == pytest.approx(0.5)


def test_brake_line_effective_radius(brake_line: BrakeLine) -> None:
    assert brake_line.effective_radius == pytest.approx(0.14)


def test_brake_line_force_to_torque_scaling(brake_line: BrakeLine) -> None:
    assert brake_line.force_to_torque_scaling_factor == pytest.approx(0.035)
