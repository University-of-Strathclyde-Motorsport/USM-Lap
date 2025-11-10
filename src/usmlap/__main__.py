from vehicle.vehicle import load_vehicle
from vehicle.parameters import Parameter
from track.track_data import load_track_from_spreadsheet
from track.mesh import MeshGenerator
from simulation.simulation import SimulationSettings
from simulation.competition import CompetitionSettings
from analysis.sweep_1d import sweep_1d, SweepSettings
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


# sweep_settings = SweepSettings(
#     parameter=Parameter.get_parameter("Curb Mass"),
#     start_value=194.43,
#     end_value=194.46,
#     number_of_steps=10,
# )
sweep_settings = SweepSettings(
    parameter=Parameter.get_parameter("Curb Mass"),
    start_value=190,
    end_value=200,
    number_of_steps=10,
)
# sweep_results = sweep_1d(
#     baseline_vehicle=vehicle,
#     sweep_settings=sweep_settings,
#     competition_settings=competition_settings,
# )
# sweep_results.plot()
coupling_results = coupling(
    baseline_vehicle=vehicle,
    sweep_settings=sweep_settings,
    coupled_parameter=Parameter.get_parameter("Drag Coefficient"),
    competition_settings=competition_settings,
)
coupling_results.plot()
