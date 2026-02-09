import logging

from simulation.competition import CompetitionSettings
from simulation.plots import plot_channels
from simulation.simulation import SimulationSettings, simulate
from track.mesh import MeshGenerator
from track.track_data import load_track_from_spreadsheet
from vehicle.vehicle import load_vehicle

logging.basicConfig(
    level=logging.WARN,
    format="{asctime} {levelname}: {message}",
    style="{",
    datefmt="%H:%M:%S",
)
# logging.getLogger("simulation.solver.quasi_steady_state").setLevel(
#     logging.INFO
# )

vehicle = load_vehicle("USM23 Baseline.json")
track_data = load_track_from_spreadsheet("FS AutoX Germany 2012.xlsx")

mesh = MeshGenerator(resolution=1).generate_mesh(track_data)
simulation_settings = SimulationSettings()
competition_settings = CompetitionSettings(
    autocross_track=track_data, simulation_settings=simulation_settings
)

simulation_results = simulate(vehicle, mesh, simulation_settings)
# plot_apexes(simulation_results)
plot_channels(
    simulation_results,
    [
        "Velocity",
        "Drag",
        "Longitudinal Acceleration",
        "Lateral Acceleration",
        "Resultant Acceleration",
    ],
)
logging.info(f"Total time: {simulation_results.total_time:.3f}s")

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
# plot GGV
