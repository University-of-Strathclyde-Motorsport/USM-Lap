"""
This script simulates the skidpad event.
"""

from pathlib import Path

from usmlap.competition.events.skidpad import Skidpad
from usmlap.plot.apex import plot_apexes
from usmlap.simulation.settings import SimSettings
from usmlap.vehicle.vehicle import Vehicle

skidpad = Skidpad()

vehicle = Vehicle.from_json("USM26")

settings = SimSettings.from_yaml(Path("sims/basic_simulation.yaml"))
solution = skidpad.simulate_event(vehicle, settings)
plot_apexes(solution)
