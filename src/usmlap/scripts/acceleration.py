"""
This script simulates the skidpad event.
"""

from pathlib import Path

from usmlap.competition.events.acceleration import Acceleration
from usmlap.plot.apex import plot_apexes
from usmlap.simulation.settings import SimSettings
from usmlap.vehicle.vehicle import Vehicle

acceleration = Acceleration()

vehicle = Vehicle.from_file(Path(r"data\vehicles\USM26.json"))

settings = SimSettings.from_file(Path("sims/basic_simulation.yaml"))

solution = acceleration.simulate_event(vehicle, settings)
plot_apexes(solution)
