"""
Code for profiling the performance of the simulation.
"""

import cProfile
import pstats

from usmlap.simulation.simulation import SimulationSettings, simulate
from usmlap.simulation.solver.quasi_transient import QuasiTransientSolver
from usmlap.track.mesh import MeshGenerator
from usmlap.track.track_data import load_track_from_spreadsheet
from usmlap.vehicle.vehicle import load_vehicle

track_sheet = "FS AutoX Germany 2012.xlsx"
track_data = load_track_from_spreadsheet(track_sheet)
mesh = MeshGenerator(resolution=0.1).generate_mesh(track_data)

vehicle = load_vehicle("USM23 Baseline.json")
simulation_settings = SimulationSettings(solver=QuasiTransientSolver)

cProfile.run(
    statement="simulate(vehicle, mesh, simulation_settings)", filename="restats"
)
p = pstats.Stats("restats")
p.strip_dirs().sort_stats(pstats.SortKey.TIME).print_stats()
