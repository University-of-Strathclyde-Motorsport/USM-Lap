"""
This script displays a velocity profile from a simulation."""

from pathlib import Path

from usmlap.plot.apex import plot_apexes
from usmlap.simulation.settings import SimSettings
from usmlap.simulation.simulation import get_initial_state, simulate
from usmlap.track.mesh_generation import generate_mesh
from usmlap.vehicle.vehicle import Vehicle

VEHICLE_FILE = Path(r"data\vehicles\USM26.json")
settings = SimSettings.from_file(Path(r"sims/basic_simulation.yaml"))


def main() -> None:
    """
    Main function."""
    mesh = generate_mesh(settings.outings[0].track)
    vehicle = Vehicle.from_file(VEHICLE_FILE)
    results = simulate(vehicle, mesh, settings, get_initial_state(settings))
    plot_apexes(results)


if __name__ == "__main__":
    main()
