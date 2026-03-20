"""
Main entry point for the program.
"""

import logging
import time

from usmlap.analysis import SweepSettings, coupling
from usmlap.competition import Competition
from usmlap.plot import plot_apexes
from usmlap.simulation import SimulationSettings, simulate
from usmlap.simulation.solver import QuasiTransientSolver
from usmlap.track import MeshGenerator, load_track_from_spreadsheet
from usmlap.vehicle import load_vehicle
from usmlap.vehicle.parameters import DragCoefficient, LiftCoefficient

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
logging.getLogger("simulation.model.point_mass").setLevel(logging.DEBUG)

# track_sheet = "Spa-Francorchamps.xlsx"
track_sheet = "FS AutoX Germany 2012.xlsx"
track_data = load_track_from_spreadsheet(track_sheet)
mesh = MeshGenerator(resolution=0.1).generate_mesh(track_data)

vehicle = load_vehicle("USM23 Baseline.json")
print(vehicle)
simulation_settings = SimulationSettings(solver=QuasiTransientSolver)

# start_time = time.time()
results = simulate(vehicle, mesh, simulation_settings)
print(f"Total time: {results.total_time:.3f}s")

plot_apexes(results)

# competition_settings = CompetitionSettings(
#     autocross_track="FS AutoX Germany 2012.xlsx"
# )
# competition = Competition(simulation_settings, competition_settings)
# sweep_settings = SweepSettings(
#     parameter=LiftCoefficient, start_value=3, end_value=6, number_of_steps=10
# )


# results = coupling(vehicle, competition, sweep_settings, DragCoefficient)
# results.plot()
