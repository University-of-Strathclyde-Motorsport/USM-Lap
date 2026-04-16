"""
This script displays a velocity profile from a simulation.
"""

from usmlap.model.vehicle import Bicycle
from usmlap.plot import plot_apexes
from usmlap.simulation import SimulationSettings, simulate
from usmlap.simulation.solver import QuasiTransientSolver
from usmlap.track import TrackData, generate_mesh
from usmlap.vehicle import Vehicle

TRACK_SHEET = "FS AutoX Germany 2012"
VEHICLE_FILE = "USM26"
SOLVER = QuasiTransientSolver
VEHICLE_MODEL = Bicycle


def main() -> None:
    """Main function."""

    track_data = TrackData.from_json(TRACK_SHEET)
    mesh = generate_mesh(track_data, resolution=0.1)
    vehicle = Vehicle.from_json(VEHICLE_FILE)
    simulation_settings = SimulationSettings(
        solver=SOLVER, vehicle_model=VEHICLE_MODEL
    )

    results = simulate(vehicle, mesh, simulation_settings)
    plot_apexes(results)


if __name__ == "__main__":
    main()
