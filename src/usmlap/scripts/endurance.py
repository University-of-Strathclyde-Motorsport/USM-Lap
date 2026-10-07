"""
This script simulates the skidpad event.
"""

from pathlib import Path

from usmlap.competition.events.endurance import Endurance
from usmlap.plot.telemetry import plot_channels
from usmlap.simulation.settings import SimSettings
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

settings = SimSettings.from_yaml(Path("sims/basic_simulation.yaml"))

endurance = Endurance(Path(r"data\tracks\FS AutoX Germany 2012.json"))

vehicle = Vehicle.from_json("USM26")


solution = endurance.simulate_event(vehicle, settings)

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
