"""
This script simulates the skidpad event.
"""

from usmlap.competition.events import Endurance
from usmlap.plot import plot_channels
from usmlap.simulation.channels.library import (
    ResultantAcceleration,
    StateOfCharge,
    Velocity,
)
from usmlap.simulation.settings import QualityPresets
from usmlap.vehicle import Vehicle

QUALITY = QualityPresets.FAST

endurance = Endurance(track_file="FS AutoX Germany 2012")

vehicle = Vehicle.from_json("USM26")


solution = endurance.simulate_event(vehicle, QUALITY)

plot_channels(
    {"": solution},
    [Velocity, ResultantAcceleration, StateOfCharge],
    show_legend=False,
)
