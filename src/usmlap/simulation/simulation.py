"""
This module contains code for running a simulation."""

from __future__ import annotations

import logging

from rich import progress

from usmlap.core.log import log_to_file
from usmlap.io.filemap import OutingFileMap, SimGroupFileMap, StudyFileMap
from usmlap.io.parquet import write_parquet
from usmlap.io.sim_folder import get_unique_filepath
from usmlap.model.vehicle_state import TransientVariables
from usmlap.plot.generate_plots import generate_plots
from usmlap.simulation.settings import OutingSettings, SimSettings
from usmlap.simulation.study import Study
from usmlap.solver.solution import create_new_solution
from usmlap.solver.solution_channels import SolutionDataFrame
from usmlap.telemetry.data.solution import TelemetrySolution
from usmlap.track.mesh import Mesh
from usmlap.track.mesh_generation import generate_mesh
from usmlap.vehicle.powertrain.cell import StateOfCharge
from usmlap.vehicle.vehicle import Vehicle

logger = logging.getLogger(__name__)


def simulate(
    vehicle: Vehicle,
    track_mesh: Mesh,
    settings: SimSettings,
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

    vehicle_model = settings.vehicle.vehicle_model.build_vehicle_model()
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


def run_study(study: Study, filemap: StudyFileMap) -> None:
    """Run a study consisting of a set of simulations."""
    logger.info("Running study %s", study.study_name)
    study.write_file(filemap.study_file)

    for settings in progress.track(
        study.iter_settings(),
        transient=True,
        description=f"Running study '{study.study_name}'...",
    ):
        sim_filepath = get_unique_filepath(
            filemap.sims_folder / settings.sim_name
        )
        sim_filemap = SimGroupFileMap(sim_filepath)
        run_simulation(settings, sim_filemap)


def run_simulation(settings: SimSettings, filemap: SimGroupFileMap) -> None:
    """Run a simulation and save the results to a file."""
    settings.vehicle.parameters.write_file(filemap.vehicle_file)
    settings.write_file(filemap.settings_file)

    for outing in settings.outings:
        outing_filepath = get_unique_filepath(filemap.root / outing.id)
        outing_filemap = OutingFileMap(outing_filepath)
        run_outing(settings, outing, outing_filemap)


def run_outing(
    settings: SimSettings, outing: OutingSettings, filemap: OutingFileMap
) -> None:
    """Run a single simulation outing."""
    outing.write_file(filemap.settings_file)

    with log_to_file(filemap.log_file):
        logger.info("Setting up simulation...")
        track_mesh = generate_mesh(outing.track)
        initial_state = get_initial_state(settings)

        logger.info("Running simulation...")
        solution = simulate(
            vehicle=settings.vehicle.parameters,
            track_mesh=track_mesh,
            settings=settings,
            initial_state=initial_state,
        )
        df_sol = SolutionDataFrame.from_solution(solution.solution)
        write_parquet(df_sol, filemap.parquet_file)

        generate_plots(filemap, settings.plots, solution=df_sol)


def get_initial_state(settings: SimSettings) -> TransientVariables:
    """Get the initial vehicle state for the simulation."""
    cell_temperature = settings.boundary_conditions.initial_cell_temperature
    if cell_temperature is None:
        cell_temperature = settings.vehicle.environment.ambient_temperature
    return TransientVariables(
        soc=StateOfCharge(settings.boundary_conditions.initial_soc),
        cell_temperature=cell_temperature,
    )
