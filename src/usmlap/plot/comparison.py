"""
This submodule contains functions for plotting comparisons between vehicles.
"""

from itertools import cycle

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


def plot_competition_bar_chart(comparison_results: ComparisonResults) -> None:
    """
    Plot a bar chart of points for a list of vehicles.

    Args:
        comparison_results (ComparisonResults): Comparison results to plot.
    """

    points_data = comparison_results.get_points()
    plot_data = _transform_data(points_data)
    vehicle_count = len(points_data)
    vehicle_labels = comparison_results.get_vehicle_labels()
    print(vehicle_labels)
    colours = cycle(["#003366", "#69C2CD", "#F5E075", "#FD9055", "#FF6454"])

    _, ax = plt.subplots()

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

    # Add some space to the left and right of the plot
    xlim_low, xlim_high = ax.get_xlim()
    ax.set_xlim(xlim_low - 0.7, xlim_high + 0.7)

    ax.yaxis.set_major_locator(MultipleLocator(100))
    ax.yaxis.set_minor_locator(MultipleLocator(20))
    ax.grid(which="both", axis="y", zorder=0)
    ax.grid(which="minor", axis="y", alpha=0.3)

    ax.legend(loc="upper right")
    plt.tight_layout
    plt.show()
