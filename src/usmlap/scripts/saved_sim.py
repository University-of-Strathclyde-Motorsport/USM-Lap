"""
This script runs a simulation which is saved to disk.
"""

from usmlap.core.filepath import TEMPORARY_ROOT
from usmlap.simulation.settings import QualityPresets
from usmlap.simulation.simulation import run_simulation
from usmlap.track import TrackData, generate_mesh
from usmlap.vehicle import Vehicle


def main() -> None:  # noqa: S1720
    vehicle = Vehicle.from_json("USM26")
    settings = QualityPresets.FAST_QSS
    track = TrackData.from_json("FS AutoX Germany 2012")
    mesh = generate_mesh(track, resolution=1)
    run_simulation(vehicle, mesh, settings, output_path=TEMPORARY_ROOT / "sim")


if __name__ == "__main__":
    main()
