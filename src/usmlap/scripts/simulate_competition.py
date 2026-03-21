"""
Script for simulating a Formula Student competition.
"""

from usmlap.competition import Competition
from usmlap.simulation import SimulationSettings
from usmlap.vehicle import load_vehicle

VEHICLE_FILE = "USM23 Baseline.json"

competition = Competition()

vehicle = load_vehicle(VEHICLE_FILE)
simulation_settings = SimulationSettings()

points = competition.simulate(vehicle, simulation_settings)
