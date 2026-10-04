"""
This script runs a simulation which is saved to disk.
"""

from usmlap.simulation.settings import QualityPresets
from usmlap.simulation.simulation import run_simulation
from usmlap.track import TrackData, generate_mesh
from usmlap.vehicle import Vehicle


def main():
    vehicle = Vehicle.from_json("USM26")
    settings = QualityPresets.FAST_QSS
    track = TrackData.from_json("FS AutoX Germany 2012")
    mesh = generate_mesh(track, resolution=1)
    run_simulation(vehicle, mesh, settings)


if __name__ == "__main__":
    main()
