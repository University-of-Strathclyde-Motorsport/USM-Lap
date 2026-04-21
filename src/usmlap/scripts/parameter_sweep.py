"""
This script runs a one-dimensional sweep of a vehicle parameter.
"""

import numpy as np

from usmlap.analysis import (
    SweepSettings,
    VehicleGenerator,
    sweep_1d,
    sweep_vehicles,
)
from usmlap.competition import Competition, CompetitionData, CompetitionPoints
from usmlap.competition.events import Acceleration, Autocross
from usmlap.plot import plot_channels, plot_points_sensitivity
from usmlap.plot.style import USM_BLUE, USM_LIGHT_BLUE, USM_ORANGE, USM_RED
from usmlap.simulation.channels import Channel
from usmlap.simulation.channels.library import (
    LongitudinalAcceleration,
    MotorPower,
    MotorTorque,
    Velocity,
)
from usmlap.simulation.settings import QualityPresets
from usmlap.solver import Solution
from usmlap.vehicle import Vehicle
from usmlap.vehicle.parameters import CoolingCoefficient, FinalDriveRatio

BASELINE_VEHICLE = "USM26"
PARAMETER = FinalDriveRatio
START_VALUE = 2.5
END_VALUE = 4
NUMBER_OF_STEPS = 30
# PARAMETER = CoolingCoefficient
# START_VALUE = 0.01
# END_VALUE = 100
# NUMBER_OF_STEPS = 10
# VALUES: list[float] = np.linspace(
#     START_VALUE, END_VALUE, NUMBER_OF_STEPS
# ).tolist()
VALUES = [2.8, 3.3, 3.8]
QUALITY = QualityPresets.FAST
baseline_vehicle = Vehicle.from_json(BASELINE_VEHICLE)
channels: list[Channel] = [
    Velocity(),
    LongitudinalAcceleration(),
    MotorTorque(),
    MotorPower(),
]

vehicles = VehicleGenerator(baseline_vehicle, FinalDriveRatio, VALUES)
event = Autocross("FS AutoX Germany 2012")
dataset = CompetitionData.from_json("FSG 2025 Hybrid")
# results = sweep_vehicles(vehicles, QUALITY)


all_points: dict[float, CompetitionPoints] = {}
results: dict[str, Solution] = {}
for vehicle in vehicles:
    fdr = vehicle.transmission.final_drive_ratio
    result = event.simulate_event(vehicle, QUALITY)
    points = event.calculate_points(result, dataset)
    all_points[vehicle.transmission.final_drive_ratio] = points
    results[str(fdr)] = result

plot_channels(
    results,
    channels,
    colours=[USM_BLUE, USM_RED, USM_LIGHT_BLUE],
    title="FDR Comparison - Autocross",
    legend_title="FDR",
    y_label_rotation="horizontal",
)

# plot_data = dict(zip(VALUES, results))
# plot_data = {value: result for value, result in zip(VALUES, results)}

# plot_points_sensitivity(FinalDriveRatio, all_points, title="Autocross Points")
# competition = Competition()

# sweep_settings = SweepSettings(PARAMETER, VALUES)

# results = sweep_1d(vehicle, QUALITY, competition, sweep_settings)
# plot_points_sensitivity(PARAMETER, results)
