"""
This module contains code for plotting telemetry data.
"""

from itertools import cycle
from typing import Literal, Optional

import matplotlib.pyplot as plt

from usmlap.telemetry import DataChannel, TelemetryChannel, TelemetrySolution
from usmlap.telemetry.channel.library import Position, Time

from .errors import NoChannelsError
from .style import COLOURMAP
from .utils import outside_legend

X_AXIS_OPTIONS = Literal["Position", "Time", "Lap"]
X_AXIS_CHANNELS: dict[X_AXIS_OPTIONS, TelemetryChannel] = {
    "Position": Position(),
    "Time": Time(),
    # "Lap": PlotLap(),
}

ROTATION_OPTIONS = Literal["vertical", "horizontal"]

LINESTYLES = Literal["solid", "dotted", "dashed", "dashdot"]


def plot_channels(
    solutions: TelemetrySolution | dict[str, TelemetrySolution],
    channels: list[DataChannel],
    *,
    x_axis: X_AXIS_OPTIONS = "Position",
    title: Optional[str] = None,
    colours: Optional[list[str]] = None,
    linestyle: LINESTYLES | list[LINESTYLES] = "solid",
    show_legend: bool = True,
    legend_title: Optional[str] = None,
    y_label_rotation: Optional[ROTATION_OPTIONS] = None,
    show_sectors: bool = False,
    wrap_width: int = 20,
) -> None:
    """
    Plot traces of telemetry channels.

    Args:
        solutions (TelemetrySolution | dict[str, TelemetrySolution]): The solutions to plot traces for.
        channels (list[DataChannel]): The channels to plot.
        x_axis (Literal["Position", "Time"]): The channel to plot on the x-axis (default = "Time").
        title (Optional[str]): The title to display above the plot.
        colours (Optional[list[str]]): The colours to use for the traces.
        linestyle (LINESTYLES | list[LINESTYLES]): The linestyle to use for the traces.
        show_legend (bool): Whether to show a legend (default = True).
        legend_title (Optional[str]): The title to use for the legend (default = None).
        y_label_rotation (Optional[Literal["vertical", "horizontal"]]): The rotation of the y-axis labels.
        show_sectors (bool): Whether to show sector boundaries (default = False).
        wrap_width (int): The width at which to wrap the y-axis labels (default = 20).
    """

    if len(channels) == 0:
        raise NoChannelsError

    if isinstance(solutions, TelemetrySolution):
        solutions = {"": solutions}
        show_legend = False

    if colours is None:
        colourmap = COLOURMAP
    else:
        colourmap = iter(colours)

    if isinstance(linestyle, str):
        linestyle = [linestyle]
    linestyles = cycle(linestyle)

    x_channel = X_AXIS_CHANNELS[x_axis]

    axs = _create_axs(
        channels,
        x_channel,
        y_label_rotation=y_label_rotation,
        wrap_width=wrap_width,
    )

    for label, solution in solutions.items():
        colour = next(colourmap)
        linestyle = next(linestyles)
        for i, y_channel in enumerate(channels):
            axs[i].plot(
                x_channel(solution),
                y_channel(solution),
                label=label,
                color=colour,
                linestyle=linestyle,
            )

    if show_sectors and x_axis == "Position":
        draw_sector_boundaries(axs, list(solutions.values())[0])

    if title is not None:
        plt.suptitle(title)

    if show_legend:
        outside_legend(axs, title=legend_title)

    plt.tight_layout()
    plt.show()


def _create_axs(
    channels: list[TelemetryChannel],
    x_channel: TelemetryChannel,
    y_label_rotation: Optional[ROTATION_OPTIONS] = None,
    wrap_width: int = 20,
) -> list[plt.Axes]:
    """Construct a set of axes for plotting telemetry channels."""
    _, axs = plt.subplots(nrows=len(channels), sharex=True)
    if isinstance(axs, plt.Axes):
        axs = [axs]

    if y_label_rotation is None:
        if len(channels) > 4:
            y_label_rotation = "horizontal"
        else:
            y_label_rotation = "vertical"

    y_label_alignment = get_label_alignment(y_label_rotation)

    for i, channel in enumerate(channels):
        axs[i].set_ylabel(
            channel.label_with_unit(wrap_width=wrap_width),
            rotation=y_label_rotation,
            horizontalalignment=y_label_alignment,
        )
        axs[i].grid()

    axs[-1].set_xlabel(x_channel.label_with_unit())

    return axs


def get_label_alignment(rotation: ROTATION_OPTIONS) -> str:
    """Get the alignment of y-axis labels."""
    match rotation:
        case "vertical":
            return "center"
        case "horizontal":
            return "right"
        case _:
            raise ValueError


def draw_sector_boundaries(
    axs: list[plt.Axes], solution: TelemetrySolution
) -> None:
    """Draw vertical lines at sector boundaries."""
    sector_boundaries = solution.get_sector_boundary_positions()
    for ax in axs:
        for sector_boundary in sector_boundaries:
            ax.axvline(
                sector_boundary, color="black", linewidth=1, linestyle="dashed"
            )
