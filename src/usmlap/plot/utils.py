"""
Utility functions for matplotlib.
"""

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
