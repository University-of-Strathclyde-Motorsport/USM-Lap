import pytest
from usmlap.vehicle.steering import Steering


@pytest.fixture
def steering() -> Steering:
    return Steering(steering_ratio=5, steering_wheel_radius=0.2)


def test_steering_wheel_angle(steering: Steering) -> None:
    assert steering.get_steering_wheel_angle(wheel_angle=0) == 0
    assert steering.get_steering_wheel_angle(wheel_angle=2) == 10
    assert steering.get_steering_wheel_angle(wheel_angle=-2) == -10


def test_wheel_angle(steering: Steering) -> None:
    assert steering.get_wheel_angle(steering_wheel_angle=0) == 0
    assert steering.get_wheel_angle(steering_wheel_angle=10) == 2
    assert steering.get_wheel_angle(steering_wheel_angle=-10) == -2
