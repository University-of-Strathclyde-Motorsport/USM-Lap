"""
This script simulates the autocross event.
"""

from pathlib import Path

from usmlap.competition.events import Autocross
from usmlap.plot.apex import plot_apexes
from usmlap.simulation.settings import QualityPresets
from usmlap.vehicle import Vehicle

autocross = Autocross(
    track_file=Path(r"data\tracks\FS AutoX Germany 2012.json")
)

vehicle = Vehicle.from_json("USM26")

simulation_settings = QualityPresets.FAST_QSS

solution = autocross.simulate_event(vehicle, simulation_settings)
# plot_gg(solution)
# plot_ggv(solution)
plot_apexes(solution)
