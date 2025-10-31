import pytest
from usmlap.vehicle.transmission import Transmission


@pytest.fixture
def transmission() -> Transmission:
    return Transmission(final_drive_ratio=3)
