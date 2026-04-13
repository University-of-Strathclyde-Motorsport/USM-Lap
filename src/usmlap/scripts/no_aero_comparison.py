"""
This script compares the performance of the vehicle
with and without the aerodynamic package.
"""

from usmlap.competition import Competition, CompetitionPoints
from usmlap.plot import plot_points_bar_chart
from usmlap.simulation.settings import QualityPresets
from usmlap.vehicle import Vehicle

QUALITY = QualityPresets.FAST

competition = Competition()

vehicle_files: dict[str, str] = {
    "USM26 No Aero": "USM26 No Aero",
    "USM24": "USM26 with USM24 Aero",
    "USM25": "USM26 with USM25 Aero",
    "USM26": "USM26",
}

results: dict[str, CompetitionPoints] = {}
for label, vehicle_file in vehicle_files.items():
    vehicle = Vehicle.from_json(vehicle_file)
    points = competition.simulate(vehicle, QUALITY)
    results[label] = points

plot_points_bar_chart(results, title="Comparison of Aerodynamic Packages")
