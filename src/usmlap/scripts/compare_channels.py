"""
This script compares the solutions for multiple vehicles.
"""

from pathlib import Path

from usmlap.competition.events.autocross import Autocross
from usmlap.plot.telemetry import plot_channels
from usmlap.simulation.settings import QualityPresets
from usmlap.telemetry.channel.channel import TelemetryChannel
from usmlap.telemetry.channel.library import MotorTorque, Velocity
from usmlap.telemetry.data.solution import TelemetrySolution
from usmlap.vehicle.parameters import FinalDriveRatio, get_new_vehicle
from usmlap.vehicle.vehicle import Vehicle

BASELINE_VEHICLE = "USM26"
TRACK_FILE = "FS AutoX Germany 2012"
PARAMETER = FinalDriveRatio
VALUES = [2.5, 3.5]
SETTINGS = QualityPresets.FAST
CHANNELS: list[TelemetryChannel] = [Velocity(), MotorTorque()]

baseline = Vehicle.from_json(BASELINE_VEHICLE)
vehicles: dict[str, Vehicle] = {}
for value in VALUES:
    vehicles[str(value)] = get_new_vehicle(baseline, PARAMETER, value)

event = Autocross(Path(r"data\tracks\FS AutoX Germany 2012.json"))


solutions: dict[str, TelemetrySolution] = {}
for value, vehicle in vehicles.items():
    solution = event.simulate_event(vehicle, SETTINGS)
    solutions[value] = solution

plot_channels(solutions, CHANNELS)
