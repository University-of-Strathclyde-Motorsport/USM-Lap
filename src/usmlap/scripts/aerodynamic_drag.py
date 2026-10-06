"""
This script shows the impact of aerodynamic drag on motor power.
"""

from pathlib import Path

from usmlap.competition.events.autocross import Autocross
from usmlap.plot.telemetry import plot_channels
from usmlap.simulation.settings import QualityPresets
from usmlap.telemetry.channel.library import Drag, MotorPower, Velocity
from usmlap.telemetry.data.solution import TelemetrySolution
from usmlap.vehicle.vehicle import Vehicle

QUALITY = QualityPresets.FAST

vehicle_files: dict[str, str] = {
    "USM24": "USM26 with USM24 Aero",
    "USM25": "USM26 with USM25 Aero",
}

autocross = Autocross(
    track_file=Path(r"data\tracks\FS AutoX Germany 2012.json")
)

results: dict[str, TelemetrySolution] = {}
for label, vehicle_file in vehicle_files.items():
    vehicle = Vehicle.from_json(vehicle_file)
    solution = autocross.simulate_event(vehicle, settings=QUALITY)
    results[label] = solution

plot_channels(
    results,
    [Velocity(), Drag(), MotorPower()],
    title="Impact of Aerodynamic Drag on Motor Power",
)
