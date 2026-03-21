"""
This module contains functions for plotting traces of channels.
"""

from typing import Literal

import matplotlib.pyplot as plt

from ..simulation.channels import Channel
from ..simulation.channels.library import Position, Time
from ..simulation.solution import Solution

X_AXIS_OPTIONS = Literal["Position", "Time"]
X_AXIS_CHANNELS: dict[X_AXIS_OPTIONS, type[Channel]] = {
    "Position": Position,
    "Time": Time,
}


def plot_channels(
    solutions: dict[str, Solution],
    channels: list[type[Channel]],
    x_axis: X_AXIS_OPTIONS = "Position",
) -> None:
    """
    Plot traces of the specified data channels.

    Args:
        solutions (list[Solution]): The solution to plot.
        channels (list[str]): The names of the data channels to plot.
        x_axis (Literal["Position", "Time"]): The function to plot on the x-axis
    """

    fig, axs = plt.subplots(nrows=len(channels), sharex=True)
    fig.suptitle("Solution")

    x_channel = X_AXIS_CHANNELS[x_axis]
    axs[-1].set_xlabel(x_channel.get_label())

    for i, channel in enumerate(channels):
        axs[i].set_ylabel(channel.get_label())
        axs[i].grid()

    for label, solution in solutions.items():
        x_data = x_channel.get_values(solution)
        for i, channel in enumerate(channels):
            y_data: list[float] = channel.get_values(solution)
            axs[i].plot(x_data, y_data, label=label)
            axs[i].set_ylabel(channel.get_label())
            axs[i].grid()

    plt.legend()
    plt.tight_layout()
    plt.show()
