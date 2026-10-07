"""
This script compares the performance of different cells.
"""

from pathlib import Path

from usmlap.analysis.vehicle_generator import VehicleGenerator
from usmlap.competition.events.endurance import Endurance
from usmlap.plot.style import USM_BLUE, USM_RED
from usmlap.plot.telemetry import plot_channels
from usmlap.simulation.settings import SimSettings
from usmlap.telemetry.channel.channel import DataChannel
from usmlap.vehicle.parameters import ElectricalCell
from usmlap.vehicle.powertrain.cell import Cell

# from usmlap.telemetry.channel.library import (
#     LapAvgCurrent,
#     LapAvgSOC,
#     LapAvgTemperature,
#     LapMaxVelocity,
#     LapTime,
# )
from usmlap.vehicle.vehicle import Vehicle

settings = SimSettings.from_yaml(Path("sims/basic_simulation.yaml"))

baseline_vehicle = Vehicle.from_json("USM26")
cells = list(Cell.library().values())

vehicles = VehicleGenerator(baseline_vehicle, ElectricalCell, cells)
endurance = Endurance(Path(r"data\tracks\FS AutoX Germany 2012.json"))
solutions = {
    vehicle.label: endurance.simulate_event(vehicle, settings)
    for vehicle in vehicles
}

# results = sweep_vehicles(vehicles, QUALITY)

# solutions = {
#     label: result.solutions["endurance"] for label, result in results.items()
# }


channels: list[DataChannel] = [
    # TODO
    # LapTime(),
    # LapMaxVelocity(),
    # LapAvgCurrent(),
    # LapAvgSOC(),
    # LapAvgTemperature(),
]

plot_channels(
    solutions,
    channels,
    x_axis="Lap",
    title="Endurance",
    colours=[USM_BLUE, USM_RED],
)
