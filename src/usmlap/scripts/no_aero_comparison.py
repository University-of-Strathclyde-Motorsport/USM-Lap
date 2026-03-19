"""
This script compares the performance of the vehicle
with and without the aerodynamic package.
"""

from usmlap.analysis.compare import compare_vehicles
from usmlap.competition.competition import Competition, CompetitionSettings
from usmlap.plot.comparison import plot_competition_bar_chart
from usmlap.simulation.simulation import SimulationSettings
from usmlap.simulation.solver.quasi_steady_state import QuasiSteadyStateSolver
from usmlap.vehicle.vehicle import load_vehicle

competition_settings = CompetitionSettings()
competition = Competition(competition_settings)

vehicle_files = ["USM26 No Aero.json", "USM24.json", "USM25.json", "USM26.json"]
vehicles = [load_vehicle(file) for file in vehicle_files]
# no_aero = load_vehicle("USM26 No Aero.json")
# baseline = load_vehicle("USM26.json")

simulation_settings = SimulationSettings(solver=QuasiSteadyStateSolver)

results = compare_vehicles(
    vehicles=vehicles,
    simulation_settings=simulation_settings,
    competition=competition,
)

plot_competition_bar_chart(results)
