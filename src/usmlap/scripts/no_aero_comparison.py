"""
This script compares the performance of the vehicle
with and without the aerodynamic package.
"""

from usmlap.competition import (
    Competition,
    CompetitionPoints,
    CompetitionSettings,
)
from usmlap.plot import plot_points_bar_chart
from usmlap.simulation.settings import QualityPresets
from usmlap.vehicle import load_vehicle

QUALITY = QualityPresets.DRAFT

competition_settings = CompetitionSettings(dataset="FSG 2025 Hybrid")
competition = Competition(competition_settings)

vehicle_files: dict[str, str] = {
    "USM26 No Aero": "USM26 No Aero.json",
    "USM24": "USM26 with USM24 Aero.json",
    "USM25": "USM26 with USM25 Aero.json",
    "USM26": "USM26.json",
}

results: dict[str, CompetitionPoints] = {}
for label, vehicle_file in vehicle_files.items():
    vehicle = load_vehicle(vehicle_file)
    points = competition.simulate(vehicle, QUALITY)
    results[label] = points

plot_points_bar_chart(results, title="Comparison of Aerodynamic Packages")
