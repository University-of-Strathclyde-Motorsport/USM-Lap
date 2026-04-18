"""
This script simulates the autocross event.
"""

from usmlap.competition.events import Autocross
from usmlap.plot import plot_apexes, plot_gg, plot_ggv
from usmlap.simulation import SimulationSettings
from usmlap.simulation.settings import QualityPresets
from usmlap.vehicle import Vehicle

autocross = Autocross(track_file="FS AutoX Germany 2012")

vehicle = Vehicle.from_json("USM26")

simulation_settings = QualityPresets.FAST

solution = autocross.simulate_event(vehicle, simulation_settings)
# plot_gg(solution)
# plot_ggv(solution)
plot_apexes(solution)
