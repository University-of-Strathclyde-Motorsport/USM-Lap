"""
This script compares the performance of different cells.
"""

from usmlap.analysis import VehicleGenerator, sweep_vehicles
from usmlap.plot import plot_channels
from usmlap.simulation.channels.library import (
    AccumulatorCurrent,
    CellTemperature,
    StateOfCharge,
    Velocity,
)
from usmlap.simulation.settings import QualityPresets
from usmlap.vehicle import Vehicle
from usmlap.vehicle.parameters import ElectricalCell
from usmlap.vehicle.powertrain import Cell

QUALITY = QualityPresets.FAST

baseline_vehicle = Vehicle.from_json("USM26")
cells = list(Cell.library().values())
vehicles = VehicleGenerator(baseline_vehicle, ElectricalCell, cells)

results = sweep_vehicles(vehicles, QUALITY)

solutions = {
    label: result.solutions["endurance"] for label, result in results.items()
}

plot_channels(
    solutions,
    [Velocity, AccumulatorCurrent, StateOfCharge, CellTemperature],
    title="Endurance",
)
