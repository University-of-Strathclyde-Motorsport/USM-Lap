"""
This module compares the performance of the QSS and QT solvers.
"""

from usmlap.competition.events import Autocross, Endurance
from usmlap.plot import plot_channels
from usmlap.plot.style import USM_BLUE, USM_RED
from usmlap.simulation import SimulationSettings, Solution
from usmlap.simulation.channels import Channel
from usmlap.simulation.channels.library import (
    LapAvgMotorTorque,
    LapAvgSOC,
    LapAvgTemperature,
    LapAvgVelocity,
    LapTime,
    MotorTorque,
    StateOfCharge,
    Velocity,
)
from usmlap.simulation.settings import QualityPresets
from usmlap.vehicle import Vehicle

configurations: dict[str, SimulationSettings] = {
    "QSS": QualityPresets.FAST_QSS,
    "QT": QualityPresets.FAST,
}

autocross_channels: list[Channel] = [Velocity(), MotorTorque(), StateOfCharge()]
endurance_channels: list[Channel] = [
    LapTime(),
    LapAvgVelocity(),
    LapAvgMotorTorque(),
    LapAvgSOC(),
    LapAvgTemperature(),
]

vehicle = Vehicle.from_json("USM26")
autocross = Autocross(track_file="FS AutoX Germany 2012")
endurance = Endurance(track_file="FS AutoX Germany 2012")

autocross_solutions: dict[str, Solution] = {}
endurance_solutions: dict[str, Solution] = {}
for label, settings in configurations.items():
    vehicle.label = label
    endurance_solutions[label] = endurance.simulate_event(
        vehicle, settings=settings
    )
    autocross_solutions[label] = autocross.simulate_event(
        vehicle, settings=settings
    )

plot_channels(
    autocross_solutions,
    autocross_channels,
    title="Solver Comparison - Autocross",
    colours=[USM_BLUE, USM_RED],
)

plot_channels(
    endurance_solutions,
    endurance_channels,
    x_axis="Lap",
    title="Solver Comparison - Endurance",
    colours=[USM_BLUE, USM_RED],
)
