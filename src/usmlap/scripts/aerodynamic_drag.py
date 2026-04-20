"""
This script shows the impact of aerodynamic drag on motor power.
"""

from usmlap.competition.events import Autocross
from usmlap.plot import plot_channels
from usmlap.simulation import Solution
from usmlap.simulation.channels.library import Drag, MotorPower, Velocity
from usmlap.simulation.settings import QualityPresets
from usmlap.vehicle import Vehicle

QUALITY = QualityPresets.FAST

vehicle_files: dict[str, str] = {
    "USM24": "USM26 with USM24 Aero",
    "USM25": "USM26 with USM25 Aero",
}

autocross = Autocross(track_file="FS AutoX Germany 2012")

results: dict[str, Solution] = {}
for label, vehicle_file in vehicle_files.items():
    vehicle = Vehicle.from_json(vehicle_file)
    solution = autocross.simulate_event(vehicle, settings=QUALITY)
    results[label] = solution

plot_channels(
    results,
    [Velocity(), Drag(), MotorPower()],
    title="Impact of Aerodynamic Drag on Motor Power",
)
