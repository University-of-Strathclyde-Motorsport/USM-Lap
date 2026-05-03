"""
This module contains utility functions for matplotlib.
"""

from typing import Optional

from matplotlib.axes import Axes


def combined_legend(*args: Axes) -> None:
    """
    Create a combined legend for multiple axes.

    Args:
        *args (Axes): The axes to create a legend for.
    """
    combined_handles = []
    combined_labels: list[str] = []

    for ax in args:
        handles, labels = ax.get_legend_handles_labels()
        combined_handles += handles
        combined_labels += labels

    args[0].legend(combined_handles, combined_labels)


def outside_legend(axs: Axes | list[Axes], title: Optional[str] = None) -> None:
    """
    Add a legend outside the plot.
    """

    if isinstance(axs, Axes):
        axs = [axs]

    for ax in axs:
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    axs[0].legend(bbox_to_anchor=(1, 1), loc="upper left", title=title)
