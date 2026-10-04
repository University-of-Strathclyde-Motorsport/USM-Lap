"""
This module plots telemetry data as a waveform.
"""

import logging

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from usmlap.plot.config import WaveformConfig
from usmlap.solver.solution_channels import SolutionDataFrame

logger = logging.getLogger(__name__)


def plot_waveform(data: SolutionDataFrame, config: WaveformConfig) -> Figure:
    """Plot a waveform."""
    if not config.axes:
        raise ValueError("Must provide at least one axes configuration")
    logger.info("Plotting waveform with config '%s'", config.title)
    fig, axs = _get_subplots(config)
    x_data = data.get_channel(config.xaxis.channel_id)

    for ax, axis_config in zip(axs, config.axes, strict=True):
        for channel_config in axis_config.channels:
            y_data = data.get_channel(channel_config.channel_id)
            ax.plot(x_data, y_data, label=channel_config.label)

        if axis_config.ylabel is not None:
            ax.set_ylabel(axis_config.ylabel)

        ax.grid(axis_config.show_grid, axis="y")

        if axis_config.show_legend:
            ax.legend()
        # ax.tick_params(axis="x", which="both", bottom=False)

    axs[-1].set_xlim(xmin=min(x_data), xmax=max(x_data))

    fig.suptitle(config.title)
    return fig


def _get_subplots(config: WaveformConfig) -> tuple[Figure, list[plt.Axes]]:
    """Construct a matplotlib figure and subplots."""
    fig, axs = plt.subplots(
        nrows=len(config.axes), sharex=True, layout="constrained"
    )
    return fig, axs.flat
