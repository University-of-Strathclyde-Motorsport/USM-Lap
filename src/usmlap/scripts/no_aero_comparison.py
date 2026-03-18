"""
This script compares the performance of the vehicle
with and without the aerodynamic package.
"""

from usmlap.analysis.compare import compare_vehicles
from usmlap.competition.competition import Competition, CompetitionSettings
from usmlap.plot.comparison import plot_event_points
from usmlap.simulation.simulation import SimulationSettings
from usmlap.simulation.solver.quasi_steady_state import QuasiSteadyStateSolver
from usmlap.vehicle.vehicle import load_vehicle

competition_settings = CompetitionSettings()
competition = Competition(competition_settings)

baseline = load_vehicle("USM26.json")
no_aero = load_vehicle("USM26 No Aero.json")

simulation_settings = SimulationSettings(solver=QuasiSteadyStateSolver)

results = compare_vehicles(
    vehicles=[baseline, no_aero],
    simulation_settings=simulation_settings,
    competition=competition,
)

plot_event_points(results)
