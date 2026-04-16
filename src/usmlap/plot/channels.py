"""
This module contains functions for plotting traces of channels.
"""

from typing import Literal, Optional

import matplotlib.pyplot as plt

from ..simulation.channels import Channel
from ..simulation.channels.library import Position, Time
from ..simulation.solution import Solution
from .style import COLOURMAP

X_AXIS_OPTIONS = Literal["Position", "Time"]
X_AXIS_CHANNELS: dict[X_AXIS_OPTIONS, type[Channel]] = {
    "Position": Position,
    "Time": Time,
}


def plot_channels(
    solutions: dict[str, Solution],
    channels: list[type[Channel]],
    *,
    x_axis: X_AXIS_OPTIONS = "Position",
    title: Optional[str] = None,
    show_legend: bool = True,
) -> None:
    """
    Plot traces of the specified data channels.

    Args:
        solutions (dict[str, Solution]): A dict of labels and solutions to plot.
        channels (list[str]): The names of the data channels to plot.
        title (Optional[str]): The title to display above the plot
            (default = `None`).
        x_axis (Literal["Position", "Time"]): The channel to plot on the x-axis.
        show_legend (bool): Whether to show a legend.
    """

    _, axs = plt.subplots(nrows=len(channels), sharex=True)
    if len(channels) == 1:
        axs = [axs]

    x_channel = X_AXIS_CHANNELS[x_axis]
    axs[-1].set_xlabel(x_channel.get_label())

    for i, channel in enumerate(channels):
        axs[i].set_ylabel(channel.get_label())
        axs[i].grid()

    x_data = x_channel.get_values(solutions[list(solutions.keys())[0]])
    axs[-1].set_xlim(min(x_data), max(x_data))

    for label, solution in solutions.items():
        x_data = x_channel.get_values(solution)
        colour = next(COLOURMAP)
        for i, channel in enumerate(channels):
            y_data: list[float] = channel.get_values(solution)
            axs[i].plot(x_data, y_data, label=label, color=colour)

    if title is not None:
        axs[0].set_title(title)

    plt.tight_layout()

    if show_legend:
        for ax in axs:
            box = ax.get_position()
            ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        axs[0].legend(loc="upper left", bbox_to_anchor=(1, 1))

    plt.show()
