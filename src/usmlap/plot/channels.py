"""
This module contains functions for plotting traces of channels.
"""

from itertools import cycle
from typing import Literal, Optional

import matplotlib.pyplot as plt

from usmlap.solver import Solution

from ..simulation.channels import Channel
from ..simulation.channels.library import PlotLap, Position, Time
from .style import COLOURMAP

X_AXIS_OPTIONS = Literal["Position", "Time", "Lap"]
X_AXIS_CHANNELS: dict[X_AXIS_OPTIONS, Channel] = {
    "Position": Position(),
    "Time": Time(),
    "Lap": PlotLap(),
}
ROTATION_OPTIONS = Literal["vertical", "horizontal"]

LINESTYLES = Literal["solid", "dotted", "dashed", "dashdot"]


def plot_channels(
    solutions: dict[str, Solution],
    channels: list[Channel],
    *,
    x_axis: X_AXIS_OPTIONS = "Position",
    title: Optional[str] = None,
    colours: Optional[list[str]] = None,
    linestyle: LINESTYLES | list[LINESTYLES] = "solid",
    show_legend: bool = True,
    legend_title: Optional[str] = None,
    y_label_rotation: Optional[ROTATION_OPTIONS] = None,
    show_sectors: bool = False,
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
        y_label_rotation (Optional[Literal["vertical", "horizontal"]]):
            The rotation of the y-axis labels.
    """
    if y_label_rotation is None:
        if len(channels) > 4:
            y_label_rotation = "horizontal"
        else:
            y_label_rotation = "vertical"

    y_label_alignment = get_label_alignment(y_label_rotation)

    if colours is None:
        colourmap = COLOURMAP
    else:
        colourmap = iter(colours)

    if isinstance(linestyle, str):
        linestyle = [linestyle]
    linestyles = cycle(linestyle)

    fig, axs = plt.subplots(nrows=len(channels), sharex=True)
    if len(channels) == 1:
        axs = [axs]

    x_channel = X_AXIS_CHANNELS[x_axis]
    axs[-1].set_xlabel(x_channel.get_label(), fontsize=16)

    for i, channel in enumerate(channels):
        axs[i].set_ylabel(
            channel.get_label(),
            rotation=y_label_rotation,
            horizontalalignment=y_label_alignment,
            fontsize=16,
        )
        axs[i].grid()

    x_data = x_channel(solutions[list(solutions.keys())[0]])
    axs[-1].set_xlim(min(x_data), max(x_data))

    for label, solution in solutions.items():
        x_data = x_channel.get_values(solution)
        sector_boundary_positions = solution.get_sector_boundary_positions()
        colour = next(colourmap)
        linestyle = next(linestyles)
        for i, channel in enumerate(channels):
            y_data: list[float] = channel.get_values(solution)
            axs[i].plot(
                x_data, y_data, label=label, color=colour, linestyle=linestyle
            )
            if show_sectors:
                for sector_boundary in sector_boundary_positions:
                    axs[i].axvline(
                        sector_boundary,
                        color="black",
                        linewidth=1,
                        linestyle="dashed",
                    )

    if title is not None:
        axs[0].set_title(title, fontsize=20)

    if show_legend:
        for ax in axs:
            box = ax.get_position()
            ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
            ax.tick_params(axis="both", which="major", labelsize=16)
        axs[0].legend(
            loc="upper left",
            bbox_to_anchor=(1, 1),
            fontsize=16,
            title=legend_title,
            title_fontsize=16,
        )

    plt.show()
    plt.tight_layout()


def get_label_alignment(rotation: ROTATION_OPTIONS) -> str:
    """Get the alignment of y-axis labels."""
    match rotation:
        case "vertical":
            return "center"
        case "horizontal":
            return "right"
        case _:
            raise ValueError
