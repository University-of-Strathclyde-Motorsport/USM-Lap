"""
This script simulates the skidpad event.
"""

from pathlib import Path

from usmlap.competition.events.endurance import Endurance
from usmlap.plot.telemetry import plot_channels
from usmlap.simulation.settings import QualityPresets
from usmlap.telemetry.channel.library import (
    AccumulatorCurrent,
    CellTemperature,
    CoolingPower,
    HeatingPower,
    MotorTorque,
    NetHeatingPower,
    StateOfCharge,
    Velocity,
)
from usmlap.vehicle.vehicle import Vehicle

QUALITY = QualityPresets.FAST

endurance = Endurance(Path(r"data\tracks\FS AutoX Germany 2012.json"))

vehicle = Vehicle.from_json("USM26")


solution = endurance.simulate_event(vehicle, QUALITY)

plot_channels(
    {"": solution},
    [
        Velocity(),
        MotorTorque(),
        AccumulatorCurrent(),
        StateOfCharge(),
        CellTemperature(),
        HeatingPower(),
        CoolingPower(),
        NetHeatingPower(),
    ],
    show_legend=False,
)
