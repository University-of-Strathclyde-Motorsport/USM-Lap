"""
This module contains code for running a simulation."""

from __future__ import annotations

import logging
from pathlib import Path

from usmlap.core.filepath import OUTPUT_ROOT
from usmlap.core.log import log_to_file
from usmlap.io.filemap import FileMap
from usmlap.io.sim_folder import make_new_sim_folder
from usmlap.model import TransientVariables
from usmlap.simulation.settings import SimulationSettings
from usmlap.solver.solution import create_new_solution
from usmlap.telemetry import TelemetrySolution
from usmlap.track import Mesh
from usmlap.vehicle import Vehicle

logger = logging.getLogger(__name__)


def simulate(
    vehicle: Vehicle,
    track_mesh: Mesh,
    settings: SimulationSettings,
    initial_state: TransientVariables | None = None,
) -> TelemetrySolution:
    """
    Simulate a vehicle driving around a track.

    Args:
        vehicle (Vehicle): The vehicle to simulate.
        settings (SimulationSettings): Settings for the simulation.

    """
    if initial_state is None:
        initial_state = TransientVariables.get_default()

    vehicle_model = settings.vehicle_model.build_vehicle_model()
    global_context = settings.get_global_context(vehicle)
    solver = settings.solver(vehicle_model.traction, global_context)

    solution = create_new_solution(
        track_mesh,
        vehicle_model.traction,
        initial_state,
    )
    solution = solver.solve(solution)
    return TelemetrySolution(
        vehicle=vehicle,
        solution=solution,
        solver=type(solver),
    )


def run_simulation(output_path: Path = OUTPUT_ROOT) -> None:
    """Run a simulation and save the results to a file."""
    sim_folder = make_new_sim_folder(output_path)
    filemap = FileMap(sim_folder)
    with log_to_file(filemap.log_file):
        logger.info("Running simulation")


if __name__ == "__main__":
    run_simulation()
