"""
This script compares the performance of the vehicle
with and without the aerodynamic package.
"""

from usmlap.analysis import VehicleGenerator
from usmlap.competition import (
    Competition,
    CompetitionPoints,
    CompetitionSolutions,
)
from usmlap.competition.events import Autocross
from usmlap.plot import plot_channels, plot_gg, plot_points_bar_chart
from usmlap.plot.style import USM_BLUE, USM_LIGHT_BLUE, USM_RED
from usmlap.simulation.channels import Channel
from usmlap.simulation.channels.library import (
    AccumulatorCurrent,
    Drag,
    LateralAcceleration,
    LongitudinalAcceleration,
    MotorPower,
    Velocity,
)
from usmlap.simulation.settings import QualityPresets
from usmlap.solver import Solution
from usmlap.vehicle import Vehicle
from usmlap.vehicle.aero import AeroPackage
from usmlap.vehicle.parameters import AerodynamicPackage

QUALITY = QualityPresets.FAST
CHANNELS: list[Channel] = [
    Velocity(),
    LongitudinalAcceleration(),
    LateralAcceleration(),
]

# competition = Competition()
baseline_vehicle = Vehicle.from_json("USM26")

aero_files: dict[str, str] = {
    "No Aero": "no_aero",
    # "USM23": "USM23",
    # "USM24": "USM24",
    "USM25": "USM25",
    "USM26": "USM26",
}

packages = [AeroPackage.from_json(file) for file in aero_files.values()]
vehicles = VehicleGenerator(baseline_vehicle, AerodynamicPackage, packages)
autocross = Autocross(track_file="FS AutoX Germany 2012")

solutions: dict[str, Solution] = {}
for label, vehicle in zip(aero_files.keys(), vehicles):
    solutions[label] = autocross.simulate_event(vehicle, QUALITY)

# plot_channels(
#     solutions,
#     [Velocity(), Drag(), MotorPower(), AccumulatorCurrent()],
#     title="Comparison of Aerodynamic Packages",
# )

plot_gg(
    solutions,
    title="Comparison of Aerodynamic Packages",
    colours=[USM_RED, USM_LIGHT_BLUE, USM_BLUE],
)

# points: dict[str, CompetitionPoints] = {}
# solutions: dict[str, CompetitionSolutions] = {}
# for label, vehicle_file in vehicle_files.items():
#     vehicle = Vehicle.from_json(vehicle_file)
#     results = competition.simulate(vehicle, QUALITY)
#     points[label] = results.points
#     solutions[label] = results.solutions

# for label, vehicle in

# plot_points_bar_chart(points, title="Comparison of Aerodynamic Packages")

# autocross_solutions = {
#     label: solution["autocross"] for label, solution in solutions.items()
# }
# plot_channels(autocross_solutions, CHANNELS)

# acceleration_solutions = {
#     label: solution["acceleration"] for label, solution in solutions.items()
# }
# plot_channels(
#     acceleration_solutions,
#     [Velocity(), LongitudinalAcceleration()],
#     title="Acceleration",
# )
