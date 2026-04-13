"""
Script for simulating a Formula Student competition.
"""

from usmlap.competition import Competition
from usmlap.simulation import SimulationSettings
from usmlap.vehicle import Vehicle

VEHICLE_FILE = "USM23 Baseline"

competition = Competition()

vehicle = Vehicle.from_json(VEHICLE_FILE)
simulation_settings = SimulationSettings()

points = competition.simulate(vehicle, simulation_settings)
