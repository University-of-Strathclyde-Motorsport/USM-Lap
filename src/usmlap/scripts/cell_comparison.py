"""
This script compares the performance of different cells.
"""

from usmlap.analysis import VehicleGenerator, sweep_vehicles
from usmlap.competition.events import Endurance
from usmlap.plot import plot_channels
from usmlap.plot.style import USM_BLUE, USM_RED
from usmlap.simulation.settings import QualityPresets
from usmlap.telemetry.channel.channel import DataChannel
from usmlap.telemetry.channel.library import (
    LapAvgCurrent,
    LapAvgSOC,
    LapAvgTemperature,
    LapMaxVelocity,
    LapTime,
)
from usmlap.vehicle import Vehicle
from usmlap.vehicle.parameters import ElectricalCell
from usmlap.vehicle.powertrain import Cell

QUALITY = QualityPresets.FAST

baseline_vehicle = Vehicle.from_json("USM26")
cells = list(Cell.library().values())

vehicles = VehicleGenerator(baseline_vehicle, ElectricalCell, cells)
endurance = Endurance("FS AutoX Germany 2012")
solutions = {
    vehicle.label: endurance.simulate_event(vehicle, settings=QUALITY)
    for vehicle in vehicles
}

# results = sweep_vehicles(vehicles, QUALITY)

# solutions = {
#     label: result.solutions["endurance"] for label, result in results.items()
# }


channels: list[DataChannel] = [
    LapTime(),
    LapMaxVelocity(),
    LapAvgCurrent(),
    LapAvgSOC(),
    LapAvgTemperature(),
]

plot_channels(
    solutions,
    channels,
    x_axis="Lap",
    title="Endurance",
    colours=[USM_BLUE, USM_RED],
)
