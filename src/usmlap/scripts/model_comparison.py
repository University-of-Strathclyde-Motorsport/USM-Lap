"""
This module compares the accuracy of different vehicle models.
"""

import time

from usmlap.competition.events import Acceleration, Autocross, Skidpad
from usmlap.model import TractionModel
from usmlap.model.traction import Bicycle, FourCornerModel, PointMass
from usmlap.plot import plot_channels, plot_gg
from usmlap.plot.style import USM_BLUE, USM_LIGHT_BLUE, USM_RED
from usmlap.simulation.channels import Channel
from usmlap.simulation.channels.library import (
    Curvature,
    LateralAcceleration,
    LatLT,
    LongitudinalAcceleration,
    LongLT,
    MotorPower,
    MotorTorque,
    Velocity,
)
from usmlap.simulation.settings import QualityPresets
from usmlap.solver import Solution
from usmlap.vehicle import Vehicle

configuration = QualityPresets.FAST

vehicle_models: dict[str, type[TractionModel]] = {
    "Point Mass": PointMass,
    "Bicycle": Bicycle,
    "Four Corner": FourCornerModel,
}

plot_colours = [USM_RED, USM_LIGHT_BLUE, USM_BLUE]

acceleration_channels: list[Channel] = [
    Velocity(),
    LongitudinalAcceleration(),
    LongLT(),
    MotorTorque(),
    MotorPower(),
]
skidpad_channels: list[Channel] = [
    Curvature(),
    Velocity(),
    LateralAcceleration(),
    LatLT(),
]

autocross_channels: list[Channel] = [
    Curvature(),
    Velocity(),
    LongitudinalAcceleration(),
    LateralAcceleration(),
]

vehicle = Vehicle.from_json("USM26")

acceleration = Acceleration()
skidpad = Skidpad()
autocross = Autocross(track_file="FS AutoX Germany 2012")

acceleration_results: dict[str, Solution] = {}
skidpad_results: dict[str, Solution] = {}
autocross_results: dict[str, Solution] = {}

for label, model in vehicle_models.items():
    configuration.vehicle_model = model

    acceleration_solution = acceleration.simulate_event(vehicle, configuration)
    acceleration_results[label] = acceleration_solution

    skidpad_solution = skidpad.simulate_event(vehicle, configuration)
    skidpad_results[label] = skidpad_solution

    start_time = time.time()
    autocross_solution = autocross.simulate_event(vehicle, configuration)
    elapsed_time = time.time() - start_time
    print(f"Simulation time for {label}: {elapsed_time:.3f} s")
    autocross_results[label] = autocross_solution

print("Acceleration times:")
for label, solution in acceleration_results.items():
    print(f"{label} {solution.total_time}")

print("Skidpad times:")
for label, solution in skidpad_results.items():
    print(f"{label} {skidpad.event_time(solution)}")

print("Autocross times:")
for label, solution in autocross_results.items():
    print(f"{label} {solution.total_time}")

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

# plot_gg(
#     autocross_results,
#     title="Model Comparison - Autocross",
#     colours=plot_colours,
#     marker_size=25,
# )
