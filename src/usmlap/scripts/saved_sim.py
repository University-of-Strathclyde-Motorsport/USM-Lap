"""
This script runs a simulation which is saved to disk.
"""

from pathlib import Path

import matplotlib.pyplot as plt

from usmlap.core.filepath import TEMPORARY_ROOT
from usmlap.io.parquet import read_parquet
from usmlap.plot.config import load_plot_config
from usmlap.plot.waveform import plot_waveform
from usmlap.simulation.settings import QualityPresets
from usmlap.simulation.simulation import run_simulation
from usmlap.solver.solution_channels import SolutionDataFrame
from usmlap.track import TrackData, generate_mesh
from usmlap.vehicle import Vehicle


def main() -> None:  # noqa: S1720
    vehicle = Vehicle.from_json("USM26")
    settings = QualityPresets.FAST_QSS
    track = TrackData.from_json("FS AutoX Germany 2012")
    mesh = generate_mesh(track, resolution=1)
    filemap = run_simulation(
        vehicle, mesh, settings, output_path=TEMPORARY_ROOT / "sim"
    )

    config = load_plot_config(Path(r"plots/track_mesh.yaml"))
    data = read_parquet(filemap.parquet_file)
    _ = plot_waveform(data, config)
    plt.show()

    mesh_data = SolutionDataFrame.from_mesh(mesh)
    plot_waveform(mesh_data, config)
    plt.show()


if __name__ == "__main__":
    main()
