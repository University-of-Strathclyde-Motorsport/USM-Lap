"""
This module compares the accuracy of different vehicle models.
"""

from usmlap.competition.events import Acceleration, EventInterface, Skidpad
from usmlap.model import VehicleModelInterface
from usmlap.model.vehicle import Bicycle, FourCornerModel, PointMass
from usmlap.plot import plot_channels
from usmlap.plot.style import USM_BLUE, USM_LIGHT_BLUE, USM_RED
from usmlap.simulation import Solution
from usmlap.simulation.channels import Channel
from usmlap.simulation.channels.library import (
    LongitudinalAcceleration,
    MotorTorque,
    Velocity,
)
from usmlap.simulation.settings import QualityPresets
from usmlap.vehicle import Vehicle

configuration = QualityPresets.HIGH_QUALITY
print(configuration)

vehicle_models: dict[str, type[VehicleModelInterface]] = {
    "Point Mass": PointMass,
    "Bicycle": Bicycle,
    # "Four Corner": FourCornerModel,
}

plot_colours = [USM_BLUE, USM_RED, USM_LIGHT_BLUE]

acceleration_channels: list[Channel] = [
    Velocity(),
    LongitudinalAcceleration(),
    MotorTorque(),
]

vehicle = Vehicle.from_json("USM26")

acceleration = Acceleration()
skidpad = Skidpad()

acceleration_results: dict[str, Solution] = {}
skidpad_results: dict[str, Solution] = {}

for label, model in vehicle_models.items():
    configuration.vehicle_model = model
    print(configuration)

    acceleration_solution = acceleration.simulate_event(vehicle, configuration)
    acceleration_results[label] = acceleration_solution

    skidpad_solution = skidpad.simulate_event(vehicle, configuration)
    skidpad_results[label] = skidpad_solution


plot_channels(
    acceleration_results,
    acceleration_channels,
    title="Model Comparison - Acceleration",
    colours=plot_colours,
)

# Skidpad
# Acceleration
# GG plot
