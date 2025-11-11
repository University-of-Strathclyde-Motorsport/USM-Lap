from vehicle.vehicle import load_vehicle
from track.track_data import load_track_from_spreadsheet
from track.mesh import MeshGenerator
from simulation.simulation import SimulationSettings, simulate
from simulation.competition import CompetitionSettings
from vehicle.parameters import Parameter
from analysis.sweep_1d import SweepSettings
from analysis.coupling import coupling


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
simulation_results.plot_g()

# sweep_settings = SweepSettings(
#     parameter=Parameter.get_parameter("Curb Mass"),
#     start_value=150,
#     end_value=250,
#     number_of_steps=10,
# )
# coupling_results = coupling(
#     baseline_vehicle=vehicle,
#     sweep_settings=sweep_settings,
#     coupled_parameter=Parameter.get_parameter("Drag Coefficient"),
#     competition_settings=competition_settings,
# )
# coupling_results.plot()
