"""
This script runs a one-dimensional sweep of a vehicle parameter.
"""

import numpy as np

from usmlap.analysis import SweepSettings, sweep_1d
from usmlap.competition import Competition
from usmlap.plot import plot_points_sensitivity
from usmlap.simulation.settings import QualityPresets
from usmlap.vehicle import Vehicle
from usmlap.vehicle.parameters import CoolingCoefficient, FinalDriveRatio

BASELINE_VEHICLE = "USM26"
# PARAMETER = FinalDriveRatio
# START_VALUE = 2
# END_VALUE = 3.6
# NUMBER_OF_STEPS = 15
PARAMETER = CoolingCoefficient
START_VALUE = 0.01
END_VALUE = 100
NUMBER_OF_STEPS = 10
VALUES = np.logspace(START_VALUE, END_VALUE, NUMBER_OF_STEPS).tolist()

QUALITY = QualityPresets.FAST

vehicle = Vehicle.from_json(BASELINE_VEHICLE)

competition = Competition()

sweep_settings = SweepSettings(PARAMETER, VALUES)

results = sweep_1d(vehicle, QUALITY, competition, sweep_settings)
plot_points_sensitivity(PARAMETER, results)
