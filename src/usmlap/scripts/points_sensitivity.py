"""
This script runs a points sensitivity analysis of a vehicle parameter.
"""

from usmlap.analysis import SweepSettings, sweep_1d
from usmlap.competition import Competition, CompetitionSettings
from usmlap.plot import plot_points_sensitivity
from usmlap.simulation.settings import Presets
from usmlap.vehicle import load_vehicle
from usmlap.vehicle.parameters import FinalDriveRatio

BASELINE_VEHICLE = "USM26.json"
PARAMETER = FinalDriveRatio
START_VALUE = 1.5
END_VALUE = 3.5
NUMBER_OF_STEPS = 10
QUALITY = Presets.QUALITY

vehicle = load_vehicle(BASELINE_VEHICLE)

competition_settings = CompetitionSettings(
    dataset="FSG 2025 Hybrid", mesh_resolution=1
)
competition = Competition(competition_settings)

sweep_settings = SweepSettings(
    PARAMETER, START_VALUE, END_VALUE, NUMBER_OF_STEPS
)

results = sweep_1d(vehicle, QUALITY, competition, sweep_settings)
plot_points_sensitivity(PARAMETER, results)
