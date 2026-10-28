"""
This module creates scatter plots of telemetry data.
"""

import logging

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from usmlap.plot.config.scatter import ScatterConfig
from usmlap.solver.solution_channels import SolutionDataFrame

logger = logging.getLogger(__name__)


def plot_scatter(data: SolutionDataFrame, config: ScatterConfig) -> Figure:
    """Create a scatter plot."""

    fig, ax = plt.subplots(layout="constrained")

    x_data = data.get_channel(config.xaxis.channel_id)
    y_data = data.get_channel(config.yaxis.channel_id)
    if config.caxis is not None:
        c_data = data.get_channel(config.caxis.channel_id)
    else:
        c_data = None

    ax.scatter(
        x=x_data,
        y=y_data,
        c=c_data,  # type: ignore
        alpha=config.alpha,
    )

    ax.grid(config.show_grid)
    ax.set_xlabel(config.xaxis.label)
    ax.set_ylabel(config.yaxis.label)
    fig.suptitle(config.title)

    return fig
