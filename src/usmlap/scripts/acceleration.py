"""
This script simulates the skidpad event.
"""

from usmlap.competition.events import Acceleration
from usmlap.plot import plot_apexes
from usmlap.simulation import SimulationSettings
from usmlap.vehicle import load_vehicle

acceleration = Acceleration()

vehicle_file = "USM26.json"
vehicle = load_vehicle(vehicle_file)

simulation_settings = SimulationSettings()

solution = acceleration.simulate_event(vehicle, simulation_settings)
plot_apexes(solution)
