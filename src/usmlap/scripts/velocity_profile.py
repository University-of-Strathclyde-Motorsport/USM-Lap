"""
This script displays a velocity profile from a simulation.
"""

from usmlap.plot.apex import plot_apexes
from usmlap.simulation.simulation import SimulationSettings, simulate
from usmlap.simulation.solver.quasi_transient import QuasiTransientSolver
from usmlap.track.mesh import MeshGenerator
from usmlap.track.track_data import load_track_from_spreadsheet
from usmlap.vehicle.vehicle import load_vehicle

TRACK_SHEET = "FS AutoX Germany 2012.xlsx"
VEHICLE_FILE = "USM23 Baseline.json"


def main() -> None:
    """Main function."""

    track_data = load_track_from_spreadsheet(TRACK_SHEET)
    mesh = MeshGenerator(resolution=0.1).generate_mesh(track_data)
    vehicle = load_vehicle(VEHICLE_FILE)
    simulation_settings = SimulationSettings(solver=QuasiTransientSolver)

    results = simulate(vehicle, mesh, simulation_settings)
    plot_apexes(results)


if __name__ == "__main__":
    main()
