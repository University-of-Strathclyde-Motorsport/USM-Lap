"""
Main entry point for the program.
"""

import logging

from usmlap.analysis.sweep_1d import SweepSettings, sweep_1d
from usmlap.competition.competition import Competition
from usmlap.competition.settings import CompetitionSettings
from usmlap.simulation.simulation import SimulationSettings
from usmlap.simulation.solver.quasi_transient import QuasiTransientSolver
from usmlap.vehicle.parameters import Parameter
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

vehicle = load_vehicle("USM23 Baseline.json")
simulation_settings = SimulationSettings(solver=QuasiTransientSolver)
competition_settings = CompetitionSettings(
    autocross_track="FS AutoX Germany 2012.xlsx"
)
competition = Competition(simulation_settings, competition_settings)
sweep_settings = SweepSettings(
    parameter=Parameter.get_parameter("Curb Mass"),
    start_value=200,
    end_value=250,
    number_of_steps=10,
)

results = sweep_1d(vehicle, competition, sweep_settings)
results.plot()
