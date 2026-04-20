"""
This module defines custom errors to be raised by plot functions.
"""


class PlotError(Exception):
    """Base class for exceptions raised by plot functions."""

    ...


class NoChannelsError(PlotError):
    """Error raised when no channels are provided to a plot function."""

    def __str__(self) -> str:
        return "No channels provided to plot function."
