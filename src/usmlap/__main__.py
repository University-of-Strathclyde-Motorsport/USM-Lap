import logging

from plot.apex import plot_apexes
from plot.channels import plot_channels

from simulation.competition import CompetitionSettings
from simulation.simulation import SimulationSettings, simulate
from simulation.solver.quasi_transient import QuasiTransientSolver
from track.mesh import MeshGenerator
from track.track_data import load_track_from_spreadsheet
from vehicle.parameters import Parameter, get_new_vehicle
from vehicle.vehicle import load_vehicle

logging.basicConfig(
    level=logging.WARN,
    format="{asctime} {levelname}: {message}",
    style="{",
    datefmt="%H:%M:%S",
)
# logging.getLogger("simulation.solver.quasi_steady_state").setLevel(
#     logging.DEBUG
# )

vehicle = load_vehicle("USM23 Baseline.json")
track_data = load_track_from_spreadsheet("FS AutoX Germany 2012.xlsx")

mesh = MeshGenerator(resolution=1).generate_mesh(track_data)
simulation_settings = SimulationSettings(solver=QuasiTransientSolver)
competition_settings = CompetitionSettings(
    autocross_track=track_data, simulation_settings=simulation_settings
)

simulation_results = simulate(vehicle, mesh, simulation_settings)
print(f"Solution time: {simulation_results.total_time:.3f}s")

mass = Parameter.get_parameter("Curb Mass")
heavy_car = get_new_vehicle(vehicle, mass, 300)
heavy_results = simulate(heavy_car, mesh, simulation_settings)
print(f"Heavy time: {heavy_results.total_time:.3f}s")

plot_apexes(simulation_results)
plot_channels(
    [simulation_results, heavy_results],
    [
        "Velocity",
        "Curvature",
        "Longitudinal Acceleration",
        "Lateral Acceleration",
        "State of Charge",
    ],
    x_axis="Time",
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
