"""
This module contains code for running a simulation."""

from __future__ import annotations

import logging

from usmlap.core.log import log_to_file
from usmlap.io.filemap import SimFileMap, SimGroupFileMap
from usmlap.io.parquet import write_parquet
from usmlap.io.pydantic_io import save_object_to_json
from usmlap.io.sim_folder import get_unique_filepath
from usmlap.model.vehicle_state import TransientVariables
from usmlap.plot.generate_plots import generate_plots
from usmlap.simulation.settings import SimSettings, VehicleSettings
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


def run_simulation(settings: SimSettings, filemap: SimGroupFileMap) -> None:
    """Run a simulation and save the results to a file."""
    sim_filepath = get_unique_filepath(filemap.root / settings.sim_name)
    sim_filemap = SimFileMap(sim_filepath)

    with log_to_file(sim_filemap.log_file):
        logger.info("Setting up simulation...")
        vehicle = generate_vehicle(settings.vehicle)
        track_mesh = generate_mesh(settings.track)
        initial_state = get_initial_state(settings)

        save_object_to_json(vehicle, filemap.vehicle_file)
        settings.write_yaml(filemap.settings_file)

        logger.info("Running simulation...")
        solution = simulate(
            vehicle=vehicle,
            track_mesh=track_mesh,
            settings=settings,
            initial_state=initial_state,
        )
        df_sol = SolutionDataFrame.from_solution(solution.solution)
        write_parquet(df_sol, sim_filemap.parquet_file)

        generate_plots(sim_filemap, settings.plots, solution=df_sol)


def generate_vehicle(settings: VehicleSettings) -> Vehicle:
    """Generate a vehicle to simulate."""
    return Vehicle.from_json(settings.vehicle_file)


def get_initial_state(settings: SimSettings) -> TransientVariables:
    """Get the initial vehicle state for the simulation."""
    cell_temperature = settings.boundary_conditions.initial_cell_temperature
    if cell_temperature is None:
        cell_temperature = settings.vehicle.environment.ambient_temperature
    return TransientVariables(
        soc=StateOfCharge(settings.boundary_conditions.initial_soc),
        cell_temperature=cell_temperature,
    )
