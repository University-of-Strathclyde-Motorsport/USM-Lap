"""Generate trackmap plots of telemetry data.

https://matplotlib.org/stable/gallery/lines_bars_and_markers/multicolored_line.html
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure

from usmlap.core.colour import HexColour
from usmlap.plot.config.trackmap import TrackmapConfig
from usmlap.solver.solution_channels import ChannelId, SolutionDataFrame
from usmlap.track.coordinates import calculate_coordinates


def plot_trackmap(data: SolutionDataFrame, config: TrackmapConfig) -> Figure:
    """Plot a trackmap."""
    fig, ax = plt.subplots(layout="constrained")

    length = data.get_channel(ChannelId.LENGTH)
    curvature = data.get_channel(ChannelId.CURVATURE)
    x, y = calculate_coordinates(length, curvature)

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(segments, linewidth=config.line_width)  # ty: ignore

    if config.caxis is not None:
        c_data = data.get_channel(config.caxis.channel_id)
        lc.set_array(c_data)
        lc.set_cmap(config.caxis.cmap)
        vmin, vmax = config.caxis.get_new_clim(lc.get_clim())
        lc.set_clim(vmin, vmax)
        fig.colorbar(lc, ax=ax, label=config.caxis.label)

    ax.add_collection(lc)  # ty: ignore

    if config.show_start_line:
        _draw_start_line(ax, config.start_line_colour)

    if config.title is not None:
        ax.set_title(config.title)

    if config.show_grid:
        ax.grid(True)

    return fig


def _draw_start_line(ax: plt.Axes, colour: HexColour) -> None:
    """Plot a line at the start of the track.

    Args:
        ax (plt.Axes): The axes to draw the line on.
        colour (HexColour): The colour for the line.

    """
    ax.plot([0, 0], [-5, 5], color=colour, linewidth=3)
