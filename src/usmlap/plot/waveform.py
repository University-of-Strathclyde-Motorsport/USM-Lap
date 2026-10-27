"""
This module plots telemetry data as a waveform.
"""

import logging

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from usmlap.core.colour import HexColour, get_n_colours
from usmlap.plot.config import ChannelConfig, WaveformConfig
from usmlap.solver.solution_channels import ChannelId, SolutionDataFrame

logger = logging.getLogger(__name__)


def plot_waveform(
    data: SolutionDataFrame | list[SolutionDataFrame], config: WaveformConfig
) -> Figure:
    """Plot a waveform."""
    if not config.axes:  #  TODO: move this to config validation
        raise ValueError("Must provide at least one axes configuration")
    logger.info("Plotting waveform with config '%s'", config.title)
    fig, axs = _get_subplots(config)

    if isinstance(data, SolutionDataFrame):
        data = [data]
        colours = [None]
    else:
        colours = get_n_colours(len(data))

    for d, colour in zip(data, colours, strict=True):
        for ax, axis_config in zip(axs, config.axes, strict=True):
            for channel_config in axis_config.channels:
                _plot_channel(
                    ax=ax,
                    data=d,
                    config=channel_config,
                    x_channel=config.xaxis.channel_id,
                    override_colour=colour,
                )

            if axis_config.ylabel is not None:
                ax.set_ylabel(axis_config.ylabel)

            ax.grid(axis_config.show_grid, axis="y")

            if axis_config.show_legend:
                ax.legend()
            # ax.tick_params(axis="x", which="both", bottom=False)

    x_data = d.get_channel(config.xaxis.channel_id)
    axs[-1].set_xlim(xmin=min(x_data), xmax=max(x_data))  # TODO: sort this

    fig.suptitle(config.title)
    return fig


def _get_subplots(config: WaveformConfig) -> tuple[Figure, list[plt.Axes]]:
    """Construct a matplotlib figure and subplots."""
    heights = [axis_config.height for axis_config in config.axes]
    fig, axs = plt.subplots(
        nrows=len(config.axes),
        height_ratios=heights,
        sharex=True,
        layout="constrained",
    )
    return fig, list(axs.flat)


def _plot_channel(
    ax: plt.Axes,
    data: SolutionDataFrame,
    config: ChannelConfig,
    x_channel: ChannelId,
    *,
    override_colour: HexColour | None = None,
) -> None:
    """Plot a single channel onto the axes."""
    x_data = data.get_channel(x_channel)
    y_data = data.get_channel(config.channel_id)

    if config.gate_channel is not None:
        gate = data.get_channel(config.gate_channel).astype(np.bool)
    else:
        gate = np.full_like(x_data, True, dtype=np.bool)

    ax.plot(
        x_data[gate],
        y_data[gate],
        label=config.label,
        linestyle=config.linestyle,
        color=override_colour or config.colour,
        marker=config.marker,
        markerfacecolor=config.marker_colour,
        markeredgewidth=config.marker_edge_width,
    )
