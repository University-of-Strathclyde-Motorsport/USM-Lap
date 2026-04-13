"""
This script simulates the autocross event.
"""

from usmlap.competition.events import Autocross
from usmlap.plot import plot_apexes
from usmlap.simulation import SimulationSettings
from usmlap.vehicle import Vehicle

TRACK_FILE = "FS AutoX Germany 2012.json"

autocross = Autocross(TRACK_FILE)

vehicle = Vehicle.from_json("USM26")

simulation_settings = SimulationSettings()

solution = autocross.simulate_event(vehicle, simulation_settings)
plot_apexes(solution)
