"""Unit tests for the ``usmlap.core.datatypes`` module."""

import pytest

from usmlap.core.datatypes import *


@pytest.fixture
def front_rear_float() -> FrontRear[float]:
    return FrontRear(1.0, 2.0)


@pytest.fixture
def front_rear_string() -> FrontRear[str]:
    return FrontRear("f", "r")


@pytest.fixture
def left_right_float() -> LeftRight[float]:
    return LeftRight(1.0, 2.0)


@pytest.fixture
def left_right_string() -> LeftRight[str]:
    return LeftRight("l", "r")


@pytest.fixture
def four_corner_float() -> FourCorner[float]:
    return FourCorner(1.0, 2.0, 3.0, 4.0)


@pytest.fixture
def four_corner_string() -> FourCorner[str]:
    return FourCorner("fl", "fr", "rl", "rr")


def test_coordinate_norm():
    coord = Coordinate(x=3, y=4)
    assert coord.norm() == 5.0


def test_front_rear_addition(front_rear_float: FrontRear[float]):
    assert front_rear_float + 1 == FrontRear(2.0, 3.0)
    assert front_rear_float + front_rear_float == FrontRear(2.0, 4.0)
    with pytest.raises(TypeError):
        _ = front_rear_float + "invalid"


def test_front_rear_multiplication(front_rear_float: FrontRear[float]):
    assert front_rear_float * 2 == FrontRear(2.0, 4.0)
    assert front_rear_float * front_rear_float == FrontRear(1.0, 4.0)
    with pytest.raises(TypeError):
        _ = front_rear_float * "invalid"


def test_front_rear_normalise(front_rear_float: FrontRear[float]):
    normalised = front_rear_float.normalise()
    assert normalised == FrontRear(1 / 3, 2 / 3)


def test_front_rear_normalise_invalid(front_rear_string: FrontRear[str]):
    assert front_rear_string.normalise() is NotImplemented


def test_left_right_addition(left_right_float: LeftRight[float]):
    assert left_right_float + 1 == LeftRight(2.0, 3.0)
    assert left_right_float + left_right_float == LeftRight(2.0, 4.0)
    with pytest.raises(TypeError):
        _ = left_right_float + "invalid"


def test_left_right_multiplication(left_right_float: LeftRight[float]):
    assert left_right_float * 2 == LeftRight(2.0, 4.0)
    assert left_right_float * left_right_float == LeftRight(1.0, 4.0)
    with pytest.raises(TypeError):
        _ = left_right_float * "invalid"


def test_left_right_normalise(left_right_float: LeftRight[float]):
    normalised = left_right_float.normalise()
    assert normalised == LeftRight(1 / 3, 2 / 3)


def test_left_right_normalise_invalid(left_right_string: LeftRight[str]):
    assert left_right_string.normalise() is NotImplemented


def test_four_corner_accessors(four_corner_string: FourCorner[str]):
    assert four_corner_string.front == LeftRight("fl", "fr")
    assert four_corner_string.rear == LeftRight("rl", "rr")
    assert four_corner_string.left == FrontRear("fl", "rl")
    assert four_corner_string.right == FrontRear("fr", "rr")


def test_four_corner_addition(four_corner_float: FourCorner[float]):
    assert four_corner_float + 1 == FourCorner(2.0, 3.0, 4.0, 5.0)
    assert four_corner_float + four_corner_float == FourCorner(
        2.0, 4.0, 6.0, 8.0
    )
    with pytest.raises(TypeError):
        _ = four_corner_float + "invalid"


def test_four_corner_multiplication(
    four_corner_float: FourCorner[float],
):
    assert four_corner_float * 2 == FourCorner(2.0, 4.0, 6.0, 8.0)
    assert four_corner_float * four_corner_float == FourCorner(
        1.0, 4.0, 9.0, 16.0
    )
    with pytest.raises(TypeError):
        _ = four_corner_float * "invalid"
