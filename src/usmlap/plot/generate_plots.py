"""
This module generates plots of a simulation.
"""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pydantic import BaseModel, Field

from usmlap.core.filepath import PLOTS_ROOT
from usmlap.io.filemap import FileMap
from usmlap.io.parquet import read_parquet
from usmlap.io.plots import save_figure
from usmlap.plot.config import load_waveform_config
from usmlap.plot.scatter import load_scatter_config, plot_scatter
from usmlap.plot.waveform import plot_waveform
from usmlap.solver.solution_channels import SolutionDataFrame

logger = logging.getLogger(__name__)


class PlotSettings(BaseModel):
    """Plot settings for the simulation."""

    waveform: list[str] = Field(default_factory=list)
    scatter: list[str] = Field(default_factory=list)


@dataclass
class _PlotType[ConfigType]:
    """Configuration for plotting a specific plot type."""

    subfolder: str
    load_config_fcn: Callable[[Path], ConfigType]
    plot_fcn: Callable[[SolutionDataFrame, ConfigType], Figure]

    def get_config_filepath(self, plot_id: str) -> Path:
        return (PLOTS_ROOT / self.subfolder / plot_id).with_suffix(".yaml")


_WAVEFORM = _PlotType(
    subfolder="waveform",
    load_config_fcn=load_waveform_config,
    plot_fcn=plot_waveform,
)

_SCATTER = _PlotType(
    subfolder="scatter",
    load_config_fcn=load_scatter_config,
    plot_fcn=plot_scatter,
)


def generate_plots(
    filemap: FileMap,
    settings: PlotSettings,
    solution: SolutionDataFrame | None = None,
) -> None:
    """Generate plots of a simulation and save them to file.

    Args:
        filemap (FileMap): The filemap for the simulation.
        settings (PlotSettings): Settings for generating plots.
        solution (SolutionDataFrame | None): Optionally provide the solution.
            If not provided, it will be loaded from the filemap.
            (default = `None`)
    """
    if solution is None:
        solution = read_parquet(filemap.parquet_file)

    def _generate_plot_type(plot_ids: list[str], plot_type: _PlotType) -> None:
        for id in plot_ids:
            config_file = plot_type.get_config_filepath(id)
            if not config_file.exists():
                logger.warning("Plot '%s' not found at '%s'", id, config_file)
                continue

            config = plot_type.load_config_fcn(config_file)
            fig = plot_type.plot_fcn(solution, config)
            save_figure(fig, filemap.plots_folder / plot_type.subfolder / id)
            plt.close(fig)

    _generate_plot_type(settings.waveform, _WAVEFORM)
    _generate_plot_type(settings.scatter, _SCATTER)
