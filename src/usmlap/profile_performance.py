"""
Code for profiling the performance of the simulation.
"""

import cProfile
import pstats

from usmlap.simulation import SimulationSettings, simulate  # noqa: F401, S1128
from usmlap.simulation.solver import QuasiTransientSolver
from usmlap.track import TrackData, generate_mesh
from usmlap.vehicle import load_vehicle

track_sheet = "FS AutoX Germany 2012.json"
track_data = TrackData.from_json(track_sheet)
mesh = generate_mesh(track_data, resolution=0.1)

vehicle = load_vehicle("USM23 Baseline.json")
simulation_settings = SimulationSettings(solver=QuasiTransientSolver)

cProfile.run(
    statement="simulate(vehicle, mesh, simulation_settings)", filename="restats"
)
p = pstats.Stats("restats")
p.strip_dirs().sort_stats(pstats.SortKey.TIME).print_stats()
