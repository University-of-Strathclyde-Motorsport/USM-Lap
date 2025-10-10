import pytest
from usmlap.vehicle.transmission import Transmission


@pytest.fixture
def transmission() -> Transmission:
    return Transmission(
        primary_gear_reduction=2,
        final_gear_reduction=3,
        gear_ratios=[1, 2, 3],
    )


def test_overall_gear_ratio(transmission: Transmission) -> None:
    assert transmission.overall_gear_ratio == [6, 12, 18]
