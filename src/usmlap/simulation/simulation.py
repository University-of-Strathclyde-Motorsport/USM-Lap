"""
This module contains code for running a simulation."""

from __future__ import annotations

import logging
from pathlib import Path

from usmlap.core.filepath import OUTPUT_ROOT
from usmlap.core.log import log_to_file
from usmlap.io.filemap import FileMap
from usmlap.io.parquet import write_parquet
from usmlap.io.pydantic_io import save_object_to_json
from usmlap.io.sim_folder import make_new_sim_folder
from usmlap.model import TransientVariables
from usmlap.plot.generate_plots import generate_plots
from usmlap.simulation.settings import SimulationSettings
from usmlap.solver.solution import create_new_solution
from usmlap.solver.solution_channels import SolutionDataFrame
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


def run_simulation(
    vehicle: Vehicle,
    track_mesh: Mesh,
    settings: SimulationSettings,
    initial_state: TransientVariables | None = None,
    output_path: Path = OUTPUT_ROOT,
) -> FileMap:
    """Run a simulation and save the results to a file."""
    sim_folder = make_new_sim_folder(output_path)
    filemap = FileMap(sim_folder)
    with log_to_file(filemap.log_file):
        save_object_to_json(vehicle, filemap.vehicle_file)
        save_object_to_json(settings, filemap.settings_file)
        logger.info("Running simulation")
        solution = simulate(
            vehicle=vehicle,
            track_mesh=track_mesh,
            settings=settings,
            initial_state=initial_state,
        )
        df_sol = SolutionDataFrame.from_solution(solution.solution)
        write_parquet(df_sol, filemap.parquet_file)

        generate_plots(filemap, df_sol)

    return filemap
