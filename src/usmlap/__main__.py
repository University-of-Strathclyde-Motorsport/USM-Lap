from vehicle.vehicle import load_vehicle
from track.track_data import load_track_from_spreadsheet
from track.mesh import MeshGenerator
from simulation.simulation import SimulationSettings, simulate
from simulation.competition import CompetitionSettings

import logging

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} {levelname}: {message}",
    style="{",
    datefmt="%H:%M:%S",
)


vehicle = load_vehicle("USM23 Baseline.json")
track_data = load_track_from_spreadsheet("FS AutoX Germany 2012.xlsx")

mesh = MeshGenerator(resolution=1).generate_mesh(track_data)
simulation_settings = SimulationSettings()
competition_settings = CompetitionSettings(
    autocross_track=track_data, simulation_settings=simulation_settings
)

simulation_results = simulate(vehicle, mesh, simulation_settings)
simulation_results.plot_ggv()
