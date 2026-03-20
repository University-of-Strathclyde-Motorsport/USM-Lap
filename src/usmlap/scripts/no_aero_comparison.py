"""
This script compares the performance of the vehicle
with and without the aerodynamic package.
"""

from usmlap.analysis.compare import compare_vehicles
from usmlap.competition.competition import Competition, CompetitionSettings
from usmlap.plot.comparison import plot_competition_bar_chart
from usmlap.simulation.simulation import SimulationSettings
from usmlap.vehicle.vehicle import load_vehicle

competition_settings = CompetitionSettings(dataset="FSG 2025 Hybrid")
competition = Competition(competition_settings)

vehicle_files = [
    "USM26 No Aero.json",
    "USM26 with USM24 Aero.json",
    "USM26 with USM25 Aero.json",
    "USM26.json",
]
vehicles = [load_vehicle(file) for file in vehicle_files]

simulation_settings = SimulationSettings()

results = compare_vehicles(
    vehicles=vehicles,
    simulation_settings=simulation_settings,
    competition=competition,
)

plot_competition_bar_chart(results, title="Comparison of Aerodynamic Packages")
