"""
Main entry point for the program.
"""

import logging

from usmlap.analysis.coupling import coupling
from usmlap.analysis.sweep_1d import SweepSettings
from usmlap.competition.competition import Competition
from usmlap.competition.settings import CompetitionSettings
from usmlap.simulation.simulation import SimulationSettings
from usmlap.simulation.solver.quasi_transient import QuasiTransientSolver
from usmlap.track.mesh import MeshGenerator
from usmlap.track.track_data import load_track_from_spreadsheet
from usmlap.vehicle.parameters import DragCoefficient, LiftCoefficient
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

track_sheet = "Spa-Francorchamps.xlsx"
track_data = load_track_from_spreadsheet(track_sheet)
mesh = MeshGenerator(resolution=1).generate_mesh(track_data)
mesh.plot_map()

# vehicle = load_vehicle("USM23 Baseline.json")
# simulation_settings = SimulationSettings(solver=QuasiTransientSolver)
# competition_settings = CompetitionSettings(
#     autocross_track="FS AutoX Germany 2012.xlsx"
# )
# competition = Competition(simulation_settings, competition_settings)
# sweep_settings = SweepSettings(
#     parameter=LiftCoefficient, start_value=3, end_value=6, number_of_steps=10
# )


# results = coupling(vehicle, competition, sweep_settings, DragCoefficient)
# results.plot()
