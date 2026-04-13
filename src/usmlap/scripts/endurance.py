"""
This script simulates the skidpad event.
"""

from usmlap.competition.events import Endurance
from usmlap.plot import plot_apexes
from usmlap.simulation import SimulationSettings
from usmlap.vehicle import Vehicle

TRACK_FILE = "FS AutoX Germany 2012.json"

endurance = Endurance(TRACK_FILE)

vehicle = Vehicle.from_json("USM26")
simulation_settings = SimulationSettings()

solution = endurance.simulate_event(vehicle, simulation_settings)
plot_apexes(solution)
