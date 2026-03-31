"""
This script displays a velocity profile from a simulation.
"""

from usmlap.plot import plot_apexes
from usmlap.simulation import SimulationSettings, simulate
from usmlap.simulation.solver import QuasiTransientSolver
from usmlap.track import TrackData, generate_mesh
from usmlap.vehicle import load_vehicle

TRACK_SHEET = "FS AutoX Germany 2012.json"
VEHICLE_FILE = "USM23 Baseline.json"


def main() -> None:
    """Main function."""

    track_data = TrackData.from_json(TRACK_SHEET)
    mesh = generate_mesh(track_data, 0.1)
    vehicle = load_vehicle(VEHICLE_FILE)
    simulation_settings = SimulationSettings(solver=QuasiTransientSolver)

    results = simulate(vehicle, mesh, simulation_settings)
    plot_apexes(results)


if __name__ == "__main__":
    main()
