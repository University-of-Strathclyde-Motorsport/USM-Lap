"""
This module generates plots of a simulation.
"""

import matplotlib.pyplot as plt

from usmlap.core.filepath import PLOTS_ROOT
from usmlap.io.filemap import FileMap
from usmlap.io.parquet import read_parquet
from usmlap.io.plots import save_figure
from usmlap.plot.config import load_waveform_config
from usmlap.plot.scatter import load_scatter_config, plot_scatter
from usmlap.plot.waveform import plot_waveform
from usmlap.solver.solution_channels import SolutionDataFrame


def generate_plots(
    filemap: FileMap, solution: SolutionDataFrame | None = None
) -> None:
    """Generate plots of a simulation."""
    if solution is None:
        solution = read_parquet(filemap.parquet_file)

    for scatter_file in (PLOTS_ROOT / "scatter").iterdir():
        config = load_scatter_config(scatter_file)
        fig = plot_scatter(solution, config)
        save_figure(fig, filemap.plots_folder / "scatter" / scatter_file.stem)
        plt.close(fig)

    for waveform_file in (PLOTS_ROOT / "waveform").iterdir():
        config = load_waveform_config(waveform_file)
        fig = plot_waveform(solution, config)
        save_figure(fig, filemap.plots_folder / "waveform" / waveform_file.stem)
        plt.close(fig)
