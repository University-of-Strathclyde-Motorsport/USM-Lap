"""
This script displays a velocity profile from a simulation."""

from pathlib import Path

from usmlap.plot.apex import plot_apexes
from usmlap.simulation.settings import SimSettings
from usmlap.simulation.simulation import get_initial_state, simulate
from usmlap.track.mesh_generation import generate_mesh
from usmlap.vehicle.vehicle import Vehicle

TRACK_SHEET = "FS AutoX Germany 2012"
VEHICLE_FILE = "USM26"
settings = SimSettings.from_yaml(Path(r"sims/basic_simulation.yaml"))


def main() -> None:
    """
    Main function."""
    mesh = generate_mesh(settings.track)
    vehicle = Vehicle.from_json(VEHICLE_FILE)
    results = simulate(vehicle, mesh, settings, get_initial_state(settings))
    plot_apexes(results)


if __name__ == "__main__":
    main()
