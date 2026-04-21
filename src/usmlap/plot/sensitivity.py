"""
This module contains functions for plotting points sensitivities.
"""

import matplotlib.pyplot as plt
import numpy as np

from usmlap.competition import CompetitionPoints
from usmlap.vehicle import Parameter

from .style import COLOURMAP, USM_BLUE

type PointsData = dict[str, np.ndarray[tuple[int, ...], np.dtype[np.float32]]]


def _transform_dictionary(data: list[CompetitionPoints]) -> PointsData:
    """
    Transform points data into a suitable form for plotting.

    Args:
        data (list[CompetitionPoints]): Input points data.

    Returns:
        transformed (PointsData): Transformed points data.
    """
    events = sorted(set().union(*(d.keys() for d in data)))
    transformed: PointsData = {}
    for event in events:
        transformed[event] = np.array([d.get(event, 0) for d in data])
    return transformed


def plot_points_sensitivity(
    parameter: type[Parameter[float]],
    data: dict[float, CompetitionPoints],
    title: str = "Event Points",
) -> None:
    """
    Plot the results of a parameter sweep.

    Args:
        parameter (type[Parameter[float]]): The parameter being swept.
        data (dict[float, CompetitionPoints]):
            Dictionary of parameter values and corresponding points data.
    """

    parameter_values = list(data.keys())
    event_data = _transform_dictionary(list(data.values()))

    fig, (ax_total, ax_event) = plt.subplots(nrows=2, sharex=True)

    total_points = [sum(d.values()) for d in data.values()]
    ax_total.plot(parameter_values, total_points, label="total", color=USM_BLUE)

    for event in event_data:
        ax_event.plot(
            parameter_values,
            event_data[event],
            label=event,
            color=next(COLOURMAP),
        )

    for ax in [ax_total, ax_event]:
        ax.set_xlim(min(parameter_values), max(parameter_values))
        ax.grid()

    ax_event.set_xlabel(parameter.get_name_with_unit())
    ax_total.set_ylabel("Points")
    ax_event.set_ylabel("Points")
    ax_total.set_title("Total Points")
    ax_event.set_title(title)
    fig.suptitle(f"Points Sensitivity of {parameter.name}")

    ax_event.legend()
    plt.tight_layout()
    plt.show()
