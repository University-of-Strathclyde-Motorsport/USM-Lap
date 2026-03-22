"""
This module plots the relative magnitudes of a list of points sensitivities.
"""

from typing import Optional

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def plot_points_sensitivities(
    data: dict[str, float],
    title: str = "Points Sensitivities",
    x_label: Optional[str] = None,
) -> None:
    """
    This function plots the relative magnitudes of a list of points sensitivities.

    Args:
        data (dict[str, float]): Bar labels and corresponding sensitivities.
        title (str): Title for the plot (default = "Points Sensitivities").
        x_label (Optional[str]): Label for the x-axis (default = None).
    """
    sorted_keys = sorted(data, key=lambda x: abs(data[x]), reverse=True)
    sorted_data = {key: data[key] for key in sorted_keys}

    _, ax = plt.subplots()

    labels = list(sorted_data.keys())
    sensitivities = list(sorted_data.values())
    absolute_sensitivities = [abs(sensitivity) for sensitivity in sensitivities]
    bar_labels = [f"{sensitivity:+.2f}" for sensitivity in sensitivities]
    bar_colours = [get_bar_colour(sensitivity) for sensitivity in sensitivities]

    bars = ax.bar(labels, absolute_sensitivities, color=bar_colours, zorder=3)
    ax.bar_label(bars, labels=bar_labels, padding=3, zorder=3)

    ax.grid(which="both", axis="y", zorder=0)
    ax.grid(which="minor", axis="y", alpha=0.3)

    if x_label is not None:
        ax.set_xlabel(x_label)
    ax.set_ylabel("Points Delta")
    ax.set_title(title)

    create_legend(ax)
    plt.tight_layout()
    plt.show()


def get_bar_colour(sensitivity: float) -> str:
    """
    Get the bar colour for a sensitivity.

    If the sensitivity is positive, the bar is blue.
    If the sensitivity is negative, the bar is red.
    """
    if sensitivity > 0:
        return "#003366"
    else:
        return "#FF6454"


def create_legend(ax: plt.Axes) -> None:
    """
    Add a legend to the plot, denoting colours for positive and negative bars.
    """
    colours = {"positive": "#003366", "negative": "#FF6454"}
    labels = list(colours.keys())
    handles = [Rectangle((0, 0), 1, 1, color=colours[lab]) for lab in labels]

    ax.legend(handles, labels)
