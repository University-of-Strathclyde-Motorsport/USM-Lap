"""
This module plots the relative magnitudes of a list of points sensitivities.
"""

from dataclasses import dataclass
from functools import total_ordering
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from usmlap.plot.style import USM_BLUE, USM_RED


@total_ordering
@dataclass
class PointsSensitivityData:
    """
    Dataclass for storing points sensitivity data.

    Attributes:
        label (str): Label for the bar.

    """

    label: str
    value: float
    bar_text: str = ""

    @property
    def abs_value(self) -> float:
        return abs(self.value)

    @property
    def bar_label(self) -> str:
        return f"{self.value:+.2f}"

    @property
    def bar_colour(self) -> str:
        return get_bar_colour(self.value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, PointsSensitivityData):
            return NotImplemented
        return abs(self.value) == abs(other.value)

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, PointsSensitivityData):
            return NotImplemented
        return abs(self.value) < abs(other.value)


def plot_points_sensitivities(
    data: list[PointsSensitivityData],
    title: str = "Points Sensitivities",
    x_label: str | None = None,
    max_results: int | None = None,
) -> None:
    """
    This function plots the relative magnitudes
    of a list of points sensitivities.

    Args:
        data (dict[str, float]): Bar labels and corresponding sensitivities.
        title (str): Title for the plot (default = "Points Sensitivities").
        x_label (str | None): Label for the x-axis (default = None).
        max_results (int | None): Maximum number of bars to plot.
            If None, plot all results (default = None).

    """
    data = sorted(data, reverse=True)
    if max_results is not None:
        data = data[:max_results]

    _, ax = plt.subplots(layout="constrained")

    labels = [sensitivity.label for sensitivity in data]
    sensitivities = [sensitivity.abs_value for sensitivity in data]
    bar_labels = [sensitivity.bar_label for sensitivity in data]
    bar_text = [sensitivity.bar_text for sensitivity in data]
    bar_colours = [sensitivity.bar_colour for sensitivity in data]

    bars = ax.bar(labels, sensitivities, color=bar_colours, zorder=3)
    ax.bar_label(bars, labels=bar_labels, padding=3, zorder=3)
    ax.bar_label(
        bars,
        labels=bar_text,
        label_type="center",
        color="white",
        zorder=3,
    )

    ax.grid(which="both", axis="y", zorder=0)
    ax.grid(which="minor", axis="y", alpha=0.3)

    if x_label is not None:
        ax.set_xlabel(x_label)
    ax.set_ylabel("Points Delta")
    ax.set_title(title)

    create_legend(ax)
    plt.show()


def get_bar_colour(sensitivity: float) -> str:
    """
    Get the bar colour for a sensitivity.

    If the sensitivity is positive, the bar is blue.
    If the sensitivity is negative, the bar is red.
    """
    if sensitivity > 0:
        return USM_BLUE
    return USM_RED


def get_bar_text_colour(sensitivity: float) -> str:
    """
    Get the text colour for a sensitivity.

    If the sensitivity is positive, the text is white.
    If the sensitivity is negative, the text is black.
    """
    if sensitivity > 0:
        return "white"
    return "black"


def create_legend(ax: plt.Axes) -> None:
    """
    Add a legend to the plot, denoting colours for positive and negative bars.
    """
    colours = {
        "positive correlation": USM_BLUE,
        "negative correlation": USM_RED,
    }
    labels = list(colours.keys())
    handles = [Rectangle((0, 0), 1, 1, color=colours[lab]) for lab in labels]

    ax.legend(handles, labels)
