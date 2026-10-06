"""
This module compares the performance of the QSS and QT solvers.
"""

from pathlib import Path

from usmlap.competition.events.autocross import Autocross
from usmlap.competition.events.endurance import Endurance
from usmlap.plot.style import USM_BLUE, USM_RED
from usmlap.plot.telemetry import plot_channels
from usmlap.simulation.settings import QualityPresets, SimulationSettings
from usmlap.telemetry.channel.channel import TelemetryChannel
from usmlap.telemetry.channel.library import (
    # LapAvgMotorTorque,
    # LapAvgSOC,
    # LapAvgTemperature,
    # LapAvgVelocity,
    # LapTime,
    MotorTorque,
    StateOfCharge,
    Velocity,
)
from usmlap.telemetry.data.solution import TelemetrySolution
from usmlap.vehicle.vehicle import Vehicle

configurations: dict[str, SimulationSettings] = {
    "QSS": QualityPresets.FAST_QSS,
    "QT": QualityPresets.FAST,
}

autocross_channels: list[TelemetryChannel] = [
    Velocity(),
    MotorTorque(),
    StateOfCharge(),
]
# endurance_channels: list[TelemetryChannel] = [
#     LapTime(),
#     LapAvgVelocity(),
#     LapAvgMotorTorque(),
#     LapAvgSOC(),
#     LapAvgTemperature(),
# ]
endurance_channels: list[TelemetryChannel] = []

vehicle = Vehicle.from_json("USM26")
autocross = Autocross(Path(r"data\tracks\FS AutoX Germany 2012.json"))
endurance = Endurance(Path(r"data\tracks\FS AutoX Germany 2012.json"))

autocross_solutions: dict[str, TelemetrySolution] = {}
endurance_solutions: dict[str, TelemetrySolution] = {}
for label, settings in configurations.items():
    vehicle.label = label
    endurance_solutions[label] = endurance.simulate_event(
        vehicle,
        settings=settings,
    )
    autocross_solutions[label] = autocross.simulate_event(
        vehicle,
        settings=settings,
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
