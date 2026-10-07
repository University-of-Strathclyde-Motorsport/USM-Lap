"""
Script for simulating a Formula Student competition.
"""

from pathlib import Path

from usmlap.competition.competition import Competition
from usmlap.simulation.settings import SimSettings
from usmlap.vehicle.vehicle import Vehicle

VEHICLE_FILE = "USM23 Baseline"

competition = Competition()

vehicle = Vehicle.from_json(VEHICLE_FILE)
settings = SimSettings.from_yaml(Path("sims/basic_simulation.yaml"))

points = competition.simulate(vehicle, settings)
