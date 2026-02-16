"""
This submodule contains functions shared throughout the graph module.
"""

from functools import wraps
from typing import Any, Callable

import matplotlib.pyplot as plt

type PlotFunction = Callable[..., None]


def show_after_plotting(plot_function: PlotFunction) -> PlotFunction:
    """
    Decorator which calls plt.show() after the wrapped function.

    Use to automatically display graphs after plotting.
    """

    @wraps(plot_function)
    def wrapper(*args: tuple[Any, ...], **kwargs: dict[str, Any]) -> None:
        """Wrapper function."""
        plot_function(*args, **kwargs)
        plt.show()

    return wrapper
