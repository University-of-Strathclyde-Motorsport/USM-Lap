"""
Script for simulating a Formula Student competition.
"""

from pathlib import Path

from usmlap.competition.competition import Competition
from usmlap.simulation.settings import SimSettings
from usmlap.vehicle.vehicle import Vehicle

VEHICLE_FILE = Path(r"data\vehicles\USM23 Baseline.json")

competition = Competition()

vehicle = Vehicle.from_file(VEHICLE_FILE)
settings = SimSettings.from_file(Path("sims/basic_simulation.yaml"))

points = competition.simulate(vehicle, settings)
