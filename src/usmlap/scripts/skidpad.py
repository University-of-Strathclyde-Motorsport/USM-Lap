"""
This script simulates the skidpad event.
"""

from usmlap.competition.events import Skidpad
from usmlap.plot import plot_apexes
from usmlap.simulation import SimulationSettings
from usmlap.vehicle import Vehicle

skidpad = Skidpad()

vehicle = Vehicle.from_json("USM26")

simulation_settings = SimulationSettings()

solution = skidpad.simulate_event(vehicle, simulation_settings)
plot_apexes(solution)
