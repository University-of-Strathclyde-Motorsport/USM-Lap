"""
This submodule contains functions for plotting comparisons between vehicles.
"""

from itertools import cycle

import matplotlib.pyplot as plt
import numpy as np

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


def plot_event_points(comparison_results: ComparisonResults) -> None:
    """
    Plot a bar chart of points for a list of vehicles.

    Args:
        comparison_results (ComparisonResults): Comparison results to plot.
    """

    points_data = comparison_results.get_points()
    plot_data = _transform_data(points_data)
    vehicle_count = len(points_data)
    vehicle_labels = comparison_results.get_vehicle_labels()
    colours = cycle(["#003366", "#69C2CD", "#F5E075", "#FD9055", "#FF6454"])

    _, ax = plt.subplots()
    ax.grid(which="both", axis="y", zorder=0)

    bottom = np.zeros(vehicle_count)
    for label, points in plot_data.items():
        ax.bar(
            vehicle_labels,
            points,
            color=next(colours),
            label=label,
            bottom=bottom,
            zorder=3,
        )
        bottom += points

    ax.legend()
    plt.tight_layout
    plt.show()
