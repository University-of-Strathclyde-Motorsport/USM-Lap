"""
Main entry point for the program.
"""

import logging

from usmlap.plot import plot_apexes
from usmlap.simulation import SimulationSettings, simulate
from usmlap.simulation.solver import QuasiTransientSolver
from usmlap.track import TrackData, generate_mesh
from usmlap.vehicle import load_vehicle

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

track_sheet = "FS AutoX Germany 2012.json"
track_data = TrackData.from_json(track_sheet)
mesh = generate_mesh(track_data, 0.1)

vehicle = load_vehicle("USM23 Baseline.json")
print(vehicle)
simulation_settings = SimulationSettings(solver=QuasiTransientSolver)

results = simulate(vehicle, mesh, simulation_settings)
print(f"Total time: {results.total_time:.3f}s")

plot_apexes(results)
