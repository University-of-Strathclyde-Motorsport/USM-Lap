"""
Script for simulating a Formula Student competition.
"""

from usmlap.competition.competition import Competition, CompetitionSettings
from usmlap.simulation.simulation import SimulationSettings
from usmlap.vehicle.vehicle import load_vehicle

VEHICLE_FILE = "USM23 Baseline.json"

competition_settings = CompetitionSettings()
competition = Competition(competition_settings)

vehicle = load_vehicle(VEHICLE_FILE)
simulation_settings = SimulationSettings()

_, points = competition.simulate(vehicle, simulation_settings)
