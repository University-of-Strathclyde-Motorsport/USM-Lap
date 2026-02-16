"""
This module contains functions for plotting traces of channels.
"""

import matplotlib.pyplot as plt

from simulation.channels import get_channel, library
from simulation.solution import Solution

from .common import show_after_plotting


@show_after_plotting
def plot_channels(solutions: list[Solution], channels: list[str]) -> None:
    """
    Plot traces of the specified data channels.

    Args:
        solution (Solution): The solution to plot.
        channels (list[str]): The names of the data channels to plot.
    """

    fig, axs = plt.subplots(nrows=len(channels), sharex=True)
    fig.suptitle("Solution")

    x_channel = library.Position
    axs[-1].set_xlabel(x_channel.get_label())

    y_channels = [get_channel(channel_name) for channel_name in channels]
    for i, channel in enumerate(y_channels):
        axs[i].set_ylabel(channel.get_label())
        axs[i].grid()

    for solution in solutions:
        x_data = x_channel.get_values(solution)
        for i, channel in enumerate(y_channels):
            y_data = channel.get_values(solution)
            axs[i].plot(x_data, y_data)
            axs[i].set_ylabel(channel.get_label())
            axs[i].grid()
