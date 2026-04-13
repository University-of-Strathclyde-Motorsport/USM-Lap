"""
This script plots a list of channels over a lap.
"""

from usmlap.competition.events import Autocross
from usmlap.plot import plot_channels
from usmlap.simulation.channels.channel import Channel
from usmlap.simulation.channels.library import (
    Curvature,
    Downforce,
    MotorPower,
    StateOfCharge,
    Velocity,
)
from usmlap.simulation.settings import QualityPresets
from usmlap.vehicle import Vehicle

VEHICLE_FILE = "USM26"
TRACK_FILE = "FS AutoX Germany 2012"
SETTINGS = QualityPresets.FAST

CHANNELS: list[type[Channel]] = [
    Curvature,
    Velocity,
    Downforce,
    MotorPower,
    StateOfCharge,
]


vehicle = Vehicle.from_json(VEHICLE_FILE)
event = Autocross(track_file=TRACK_FILE)

solution = event.simulate_event(vehicle, SETTINGS)
plot_channels({"Baseline": solution}, CHANNELS, show_legend=False)
