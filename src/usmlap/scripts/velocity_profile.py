"""
This script displays a velocity profile from a simulation."""

from pathlib import Path

from usmlap.plot.apex import plot_apexes
from usmlap.simulation.settings import QualityPresets, SimSettings
from usmlap.simulation.simulation import get_initial_state, simulate
from usmlap.track.mesh_generation import generate_mesh
from usmlap.vehicle.vehicle import Vehicle

TRACK_SHEET = "FS AutoX Germany 2012"
VEHICLE_FILE = "USM26"
QUALITY = QualityPresets.DRAFT
# SOLVER = QuasiTransientSolver
# VEHICLE_MODEL = Bicycle
settings = SimSettings.from_yaml(Path(r"sims/basic_simulation.yaml"))


def main() -> None:
    """
    Main function."""
    mesh = generate_mesh(settings.track)
    vehicle = Vehicle.from_json(VEHICLE_FILE)
    # simulation_settings = SimulationSettings(
    #     solver=SOLVER, vehicle_model=VEHICLE_MODEL
    # )

    results = simulate(vehicle, mesh, QUALITY, get_initial_state(settings))
    plot_apexes(results)


if __name__ == "__main__":
    main()
