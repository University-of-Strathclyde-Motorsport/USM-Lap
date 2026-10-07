"""
This script simulates the autocross event.
"""

from pathlib import Path

from usmlap.competition.events.autocross import Autocross
from usmlap.plot.apex import plot_apexes
from usmlap.simulation.settings import SimSettings
from usmlap.vehicle.vehicle import Vehicle

autocross = Autocross(
    track_file=Path(r"data\tracks\FS AutoX Germany 2012.json")
)
settings = SimSettings.from_yaml(Path("sims/basic_simulation.yaml"))
vehicle = Vehicle.from_json("USM26")


solution = autocross.simulate_event(vehicle, settings)
# plot_gg(solution)
# plot_ggv(solution)
plot_apexes(solution)
