"""
Code for profiling the performance of the simulation."""

import cProfile
import pstats
from pathlib import Path

from usmlap.simulation.settings import SimSettings
from usmlap.simulation.simulation import simulate  # noqa: S1128 F401
from usmlap.track.mesh_generation import generate_mesh
from usmlap.track.track_data import TrackData
from usmlap.vehicle.vehicle import Vehicle

track_data = TrackData.from_json("FS AutoX Germany 2012")
settings = SimSettings.from_yaml(Path(r"sims/basic_simulation.yaml"))
mesh = generate_mesh(settings.track)

vehicle = Vehicle.from_json("USM23 Baseline")
settings = SimSettings.from_yaml(Path("sims/basic_simulation.yaml"))

cProfile.run(statement="simulate(vehicle, mesh, settings)", filename="restats")
p = pstats.Stats("restats")
p.strip_dirs().sort_stats(pstats.SortKey.TIME).print_stats()
