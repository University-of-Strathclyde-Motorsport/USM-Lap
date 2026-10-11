"""
This module creates scatter plots of telemetry data.
"""

import logging

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pydantic import BaseModel, Field

from usmlap.core.library import Serialisable
from usmlap.solver.solution_channels import ChannelId, SolutionDataFrame

logger = logging.getLogger(__name__)


class AxisConfig(BaseModel):
    """Configuration options for an axis."""

    channel_id: ChannelId
    provided_label: str | None = Field(alias="label", default=None)

    @property
    def label(self) -> str:
        return self.provided_label or self.channel_id


class ScatterConfig(Serialisable):
    """Configuration options for a scatter plot."""

    title: str
    xaxis: AxisConfig
    yaxis: AxisConfig
    caxis: AxisConfig | None = None
    alpha: float = 1
    show_grid: bool = True


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
