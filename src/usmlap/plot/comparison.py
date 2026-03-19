"""
This submodule contains functions for plotting comparisons between vehicles.
"""

from itertools import cycle
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

from usmlap.analysis.compare import ComparisonResults
from usmlap.competition.competition import CompetitionPoints

type PointsData = dict[str, np.ndarray[tuple[int, ...], np.dtype[np.float32]]]


def _transform_data(input_data: list[CompetitionPoints]) -> PointsData:
    """
    Transform points data into a format suitable for plotting.

    Args:
        input_data (list[CompetitionPoints]): Points data to transform.

    Returns:
        transformed_data (PointsData): Transformed points data.
    """

    keys = sorted(set().union(*(d.keys() for d in input_data)))
    transformed_data: PointsData = {}
    for key in keys:
        transformed_data[key] = np.array([d.get(key, 0) for d in input_data])
    return transformed_data


def plot_competition_bar_chart(
    comparison_results: ComparisonResults,
    title: str = "Comparison Results",
    padding: Optional[float] = None,
) -> None:
    """
    Plot a bar chart of points for a list of vehicles.

    Args:
        comparison_results (ComparisonResults): Comparison results to plot.
        title (str): Title for the plot.
        padding (Optional[float]): If specified, add padding
            to the left and right of the plot (default = None).
            Recommended value of 0.7.
    """

    points_data = comparison_results.get_points()
    plot_data = _transform_data(points_data)
    vehicle_count = len(points_data)
    vehicle_labels = comparison_results.get_vehicle_labels()
    colours = cycle(["#003366", "#69C2CD", "#F5E075", "#FD9055", "#FF6454"])

    fig, ax = plt.subplots()

    bottom = np.zeros(vehicle_count)
    for event, points in plot_data.items():
        ax.bar(
            vehicle_labels,
            points,
            color=next(colours),
            width=0.7,
            label=event,
            tick_label=vehicle_labels,
            bottom=bottom,
            zorder=3,
        )
        bottom += points

    if padding:
        # Add some space to the left and right of the plot
        xlim_low, xlim_high = ax.get_xlim()
        ax.set_xlim(xlim_low - padding, xlim_high + padding)

    ax.yaxis.set_major_locator(MultipleLocator(100))
    ax.yaxis.set_minor_locator(MultipleLocator(20))
    ax.grid(which="both", axis="y", zorder=0)
    ax.grid(which="minor", axis="y", alpha=0.3)

    ax.set_ylabel("Points")
    ax.set_title(title)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

    plt.tight_layout
    plt.show()
