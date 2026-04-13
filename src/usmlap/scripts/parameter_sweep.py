"""
This script runs a one-dimensional sweep of a vehicle parameter.
"""

from usmlap.analysis import SweepSettings, sweep_1d
from usmlap.competition import Competition
from usmlap.plot import plot_points_sensitivity
from usmlap.simulation.settings import QualityPresets
from usmlap.vehicle import Vehicle
from usmlap.vehicle.parameters import FinalDriveRatio

BASELINE_VEHICLE = "USM26"
PARAMETER = FinalDriveRatio
START_VALUE = 1.5
END_VALUE = 3.5
NUMBER_OF_STEPS = 10
QUALITY = QualityPresets.FAST

vehicle = Vehicle.from_json(BASELINE_VEHICLE)

competition = Competition(simulate_efficiency=False)

sweep_settings = SweepSettings(
    PARAMETER, START_VALUE, END_VALUE, NUMBER_OF_STEPS
)

results = sweep_1d(vehicle, QUALITY, competition, sweep_settings)
plot_points_sensitivity(PARAMETER, results)
