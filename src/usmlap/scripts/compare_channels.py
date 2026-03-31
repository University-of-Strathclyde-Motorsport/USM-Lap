"""
This script compares the solutions for multiple vehicles.
"""

from usmlap.competition.events import Autocross
from usmlap.plot import plot_channels
from usmlap.simulation import Solution
from usmlap.simulation.channels import Channel
from usmlap.simulation.channels.library import MotorTorque, Velocity
from usmlap.simulation.settings import QualityPresets
from usmlap.vehicle import Vehicle, get_new_vehicle, load_vehicle
from usmlap.vehicle.parameters import FinalDriveRatio

BASELINE_VEHICLE = "USM26.json"
TRACK_FILE = "FS AutoX Germany 2012.json"
PARAMETER = FinalDriveRatio
VALUES = [2.5, 3.5]
SETTINGS = QualityPresets.HIGH_QUALITY
CHANNELS: list[type[Channel]] = [Velocity, MotorTorque]

baseline = load_vehicle(BASELINE_VEHICLE)
vehicles: dict[str, Vehicle] = {}
for value in VALUES:
    vehicles[str(value)] = get_new_vehicle(baseline, PARAMETER, value)

event = Autocross(track_file=TRACK_FILE)


solutions: dict[str, Solution] = {}
for value, vehicle in vehicles.items():
    solution = event.simulate_event(vehicle, SETTINGS)
    solutions[value] = solution

plot_channels(solutions, CHANNELS)
