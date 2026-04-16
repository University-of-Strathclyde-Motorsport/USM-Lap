"""
This script compares the performance of the vehicle
with and without the aerodynamic package.
"""

from usmlap.competition import (
    Competition,
    CompetitionPoints,
    CompetitionSolutions,
)
from usmlap.plot import plot_channels, plot_points_bar_chart
from usmlap.simulation.channels import Channel
from usmlap.simulation.channels.library import (
    LateralAcceleration,
    LongitudinalAcceleration,
    Velocity,
)
from usmlap.simulation.settings import QualityPresets
from usmlap.vehicle import Vehicle

QUALITY = QualityPresets.DRAFT
CHANNELS: list[type[Channel]] = [
    Velocity,
    LongitudinalAcceleration,
    LateralAcceleration,
]

competition = Competition()

vehicle_files: dict[str, str] = {
    "USM26 No Aero": "USM26 No Aero",
    "USM23": "USM26 with USM23 Aero",
    "USM24": "USM26 with USM24 Aero",
    "USM25": "USM26 with USM25 Aero",
    "USM26": "USM26",
}

results: dict[str, CompetitionPoints] = {}
solutions: dict[str, CompetitionSolutions] = {}
for label, vehicle_file in vehicle_files.items():
    vehicle = Vehicle.from_json(vehicle_file)
    points, solution = competition.simulate(vehicle, QUALITY)
    results[label] = points
    solutions[label] = solution

plot_points_bar_chart(results, title="Comparison of Aerodynamic Packages")

autocross_solutions = {
    label: solution["autocross"] for label, solution in solutions.items()
}
plot_channels(autocross_solutions, CHANNELS)

acceleration_solutions = {
    label: solution["acceleration"] for label, solution in solutions.items()
}
plot_channels(
    acceleration_solutions,
    [Velocity, LongitudinalAcceleration],
    title="Acceleration",
)
