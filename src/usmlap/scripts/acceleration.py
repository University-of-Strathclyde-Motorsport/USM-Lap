"""
This script simulates the skidpad event.
"""

from usmlap.competition.events import Acceleration
from usmlap.plot import plot_apexes
from usmlap.simulation import SimulationSettings
from usmlap.vehicle import Vehicle

acceleration = Acceleration()

vehicle = Vehicle.from_json("USM26")

simulation_settings = SimulationSettings()

solution = acceleration.simulate_event(vehicle, simulation_settings)
plot_apexes(solution)
