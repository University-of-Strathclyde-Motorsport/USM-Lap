"""
This module contains functions for plotting comparisons between vehicles.
"""

from itertools import cycle
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

from usmlap.analysis import ComparisonResults
from usmlap.competition import CompetitionPoints

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


def _transform_dictionary(data: dict[str, CompetitionPoints]) -> PointsData:
    """
    Transform points data into a suitable form for plotting.

    Args:
        data (dict[str, CompetitionPoints]): Input points data.

    Returns:
        transformed (PointsData): Transformed points data.
    """
    events = sorted(set().union(*(d.keys() for d in data.values())))
    transformed: PointsData = {}
    for event in events:
        transformed[event] = np.array([d.get(event, 0) for d in data.values()])
    return transformed


def plot_points_bar_chart(
    data: dict[str, CompetitionPoints],
    title: str = "",
    y_label: str = "Points",
    width: float = 0.7,
) -> None:
    """
    Plot a bar chart of points for a list of simulations.

    Args:
        data (dict[str, CompetitionPoints]):
            Dictionary of bar chart labels and corresponding points data.
        title (str): Title for the plot (default = "").
        y_label (str): Label for the y-axis (default = "Points").
        width (float): Overall width of the bars (default = 0.7).
    """

    simulation_labels = data.keys()
    simulation_count = len(simulation_labels)
    points_data = _transform_dictionary(data)
    event_count = len(points_data.keys())

    x = np.arange(simulation_count)
    bar_width = width / event_count
    label_position = x + (bar_width * (event_count - 1) / 2)
    multiplier = 0
    colours = cycle(["#003366", "#69C2CD", "#F5E075", "#FD9055", "#FF6454"])

    _, ax = plt.subplots()

    for event, points in points_data.items():
        offset = bar_width * multiplier
        rects = ax.bar(
            x + offset,
            points,
            bar_width,
            label=event,
            color=next(colours),
            zorder=4,
        )
        ax.bar_label(rects, fmt="%.1f", padding=3, zorder=4)
        multiplier += 1

    total_points = [sum(points.values()) for points in data.values()]
    total_bars = ax.bar(
        label_position,
        total_points,
        width=width,
        label="total",
        color="#BBBBBB",
        zorder=3,
    )
    ax.bar_label(total_bars, fmt="%.1f", padding=3, zorder=3)

    ax.grid(which="both", axis="y", zorder=0)
    ax.grid(which="minor", axis="y", alpha=0.3)

    ax.set_xticks(label_position, simulation_labels)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc="upper left", bbox_to_anchor=(1, 1))

    plt.tight_layout
    plt.show()
