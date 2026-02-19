import logging

from usmlap.analysis.compare import compare_vehicles
from usmlap.plot.apex import plot_apexes
from usmlap.plot.channels import plot_channels
from usmlap.simulation.simulation import SimulationSettings
from usmlap.simulation.solver.quasi_transient import QuasiTransientSolver
from usmlap.track.mesh import MeshGenerator
from usmlap.track.track_data import load_track_from_spreadsheet
from usmlap.vehicle.parameters import Parameter, get_new_vehicle
from usmlap.vehicle.vehicle import load_vehicle

CHANNELS = [
    "Velocity",
    "Curvature",
    "Longitudinal Acceleration",
    "Lateral Acceleration",
    "State of Charge",
]

logging.basicConfig(
    level=logging.WARN,
    format="{asctime} {levelname}: {message}",
    style="{",
    datefmt="%H:%M:%S",
)
# logging.getLogger("simulation.solver.quasi_steady_state").setLevel(
#     logging.DEBUG
# )

track_data = load_track_from_spreadsheet("FS AutoX Germany 2012.xlsx")
mesh = MeshGenerator(resolution=1).generate_mesh(track_data)

vehicle = load_vehicle("USM23 Baseline.json")
mass = Parameter.get_parameter("Curb Mass")
heavy_car = get_new_vehicle(vehicle, mass, 300)

simulation_settings = SimulationSettings(solver=QuasiTransientSolver)
results = compare_vehicles([vehicle, heavy_car], mesh, simulation_settings)
baseline_solution = results.get_solutions()[0]

for _, solution in results:
    print(f"Total time: {solution.total_time:.3f}s")

plot_apexes(baseline_solution)
plot_channels(results.get_solutions(), CHANNELS, x_axis="Position")
