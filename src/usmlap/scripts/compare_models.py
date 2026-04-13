"""
This script compares the performance of different vehicle models.
"""

from usmlap.plot import plot_channels
from usmlap.simulation import SimulationSettings, Solution, simulate
from usmlap.simulation.channels.channel import Channel
from usmlap.simulation.channels.library import (
    LateralAcceleration,
    LongitudinalAcceleration,
    Velocity,
)
from usmlap.simulation.model import (
    BicycleVehicleModel,
    PointMassVehicleModel,
    VehicleModelInterface,
)
from usmlap.track import TrackData, generate_mesh
from usmlap.vehicle import Vehicle

VEHICLE_FILE = "USM26"
TRACK_FILE = "FS AutoX Germany 2012"
CHANNELS: list[type[Channel]] = [
    Velocity,
    LongitudinalAcceleration,
    LateralAcceleration,
]

vehicle_models: dict[str, type[VehicleModelInterface]] = {
    "Point Mass": PointMassVehicleModel,
    "Bicycle": BicycleVehicleModel,
}

vehicle = Vehicle.from_json(VEHICLE_FILE)
track_data = TrackData.from_json(TRACK_FILE)
mesh = generate_mesh(track_data, resolution=0.1)

solutions: dict[str, Solution] = {}

for label, model in vehicle_models.items():
    settings = SimulationSettings(vehicle_model=model)
    solution = simulate(vehicle, mesh, settings)
    solutions[label] = solution

plot_channels(solutions, CHANNELS)
