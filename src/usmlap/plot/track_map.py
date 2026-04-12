"""
This module contains functions for plotting track maps.
"""

from typing import Optional

from matplotlib import pyplot as plt

from usmlap.plot.style import USM_BLUE, USM_RED
from usmlap.track import Mesh


def plot_map(
    mesh: Mesh,
    ax: Optional[plt.Axes] = None,
    draw_start_arrow: bool = True,
    colour: str = USM_BLUE,
    label: Optional[str] = None,
    show_legend: bool = False,
) -> plt.Axes:
    """
    Plot a map of a track mesh.

    Args:
        mesh (Mesh): The track mesh to plot.
        ax (Optional[Axes]): The axes to plot the map on.
            If not provided, a new figure and axes will be created.
        draw_start_arrow (bool): Whether to draw an arrow
            at the start of the track (default = `True`).
        colour (str): The colour of the track (default = `USM_BLUE`).
    """

    if not ax:
        _, ax = plt.subplots()

    coordinates = [node.start_coordinate for node in mesh]
    coordinates.append(mesh.nodes[-1].end_coordinate)
    x, y = zip(*coordinates)

    ax.plot(x, y, color=colour, label=label)

    if draw_start_arrow:
        _draw_start_arrow(ax)

    ax.set_title(f"{mesh.track_name}\n{mesh.location}")
    ax.grid(True)

    if show_legend:
        ax.legend()

    return ax


def _draw_start_arrow(ax: plt.Axes) -> None:
    """
    Plot a red arrow at the start line of the track.

    Args:
        ax (Axes): The axes to draw the arrow on.
    """

    ax.plot([0, 0], [-10, 10], color=USM_RED)
    ax.annotate(
        "",
        xytext=(0, 0),
        xy=(50, 0),
        arrowprops={"arrowstyle": "->", "color": USM_RED},
    )
