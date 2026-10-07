"""
This module compares the accuracy of different vehicle models.
"""

import time
from pathlib import Path

from usmlap.competition.events.acceleration import Acceleration
from usmlap.competition.events.autocross import Autocross
from usmlap.competition.events.skidpad import Skidpad
from usmlap.model.traction.bicycle import Bicycle
from usmlap.model.traction.four_corner import FourCornerModel
from usmlap.model.traction.point_mass import PointMass
from usmlap.model.traction.traction_model import TractionModel
from usmlap.plot.ggv import plot_gg
from usmlap.plot.style import USM_BLUE, USM_LIGHT_BLUE, USM_RED
from usmlap.simulation.settings import SimSettings
from usmlap.telemetry.channel.channel import TelemetryChannel
from usmlap.telemetry.channel.library import (
    Curvature,
    LateralAcceleration,
    LatLT,
    LongitudinalAcceleration,
    LongLT,
    MotorPower,
    MotorTorque,
    Velocity,
)
from usmlap.telemetry.data.solution import TelemetrySolution
from usmlap.vehicle.vehicle import Vehicle

vehicle_models: dict[str, type[TractionModel]] = {
    "Point Mass": PointMass,
    "Bicycle": Bicycle,
    "Four Corner": FourCornerModel,
}

plot_colours = [USM_RED, USM_LIGHT_BLUE, USM_BLUE]

acceleration_channels: list[TelemetryChannel] = [
    Velocity(),
    LongitudinalAcceleration(),
    LongLT(),
    MotorTorque(),
    MotorPower(),
]
skidpad_channels: list[TelemetryChannel] = [
    Curvature(),
    Velocity(),
    LateralAcceleration(),
    LatLT(),
]

autocross_channels: list[TelemetryChannel] = [
    Curvature(),
    Velocity(),
    LongitudinalAcceleration(),
    LateralAcceleration(),
]

vehicle = Vehicle.from_json("USM26")

acceleration = Acceleration()
skidpad = Skidpad()
autocross = Autocross(Path(r"data\tracks\FS AutoX Germany 2012.json"))

acceleration_results: dict[str, TelemetrySolution] = {}
skidpad_results: dict[str, TelemetrySolution] = {}
autocross_results: dict[str, TelemetrySolution] = {}

settings = SimSettings.from_yaml(Path("sims/basic_simulation.yaml"))

for label, model in vehicle_models.items():
    settings.vehicle.vehicle_model.traction = model

    acceleration_solution = acceleration.simulate_event(vehicle, settings)
    acceleration_results[label] = acceleration_solution

    skidpad_solution = skidpad.simulate_event(vehicle, settings)
    skidpad_results[label] = skidpad_solution

    start_time = time.time()
    autocross_solution = autocross.simulate_event(vehicle, settings)
    elapsed_time = time.time() - start_time
    print(f"Simulation time for {label}: {elapsed_time:.3f} s")
    autocross_results[label] = autocross_solution

print("Acceleration times:")
for label, solution in acceleration_results.items():
    print(f"{label} {solution.solution.total_time}")

print("Skidpad times:")
for label, solution in skidpad_results.items():
    print(f"{label} {skidpad.event_time(solution)}")

print("Autocross times:")
for label, solution in autocross_results.items():
    print(f"{label} {solution.solution.total_time}")

# plot_channels(
#     acceleration_results,
#     acceleration_channels,
#     title="Model Comparison - Acceleration",
#     colours=plot_colours,
#     linestyle=["solid", "solid", "dashed"],
#     y_label_rotation="horizontal",
# )


# plot_channels(
#     skidpad_results,
#     skidpad_channels,
#     title="Model Comparison - Skidpad",
#     colours=plot_colours,
#     show_sectors=True,
# )

# plot_channels(
#     autocross_results,
#     autocross_channels,
#     title="Model Comparison - Autocross",
#     colours=plot_colours,
# )

plot_gg(
    autocross_results,
    title="Model Comparison - Autocross",
    colours=plot_colours,
    marker_size=25,
)
