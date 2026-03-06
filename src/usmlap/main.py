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

vehicle = load_vehicle("USM23 Baseline.json")
simulation_settings = SimulationSettings(solver=QuasiTransientSolver)
competition_settings = CompetitionSettings(
    autocross_track="FS AutoX Germany 2012.xlsx"
)
competition = Competition(simulation_settings, competition_settings)
sweep_settings = SweepSettings(
    parameter=LiftCoefficient, start_value=3, end_value=6, number_of_steps=10
)


results = coupling(vehicle, competition, sweep_settings, DragCoefficient)
results.plot()
