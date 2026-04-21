"""
This module contains code for plotting telemetry data.
"""

from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np

from usmlap.telemetry import TelemetryChannel, TelemetrySolution
from usmlap.telemetry.channels import DataChannel

from .errors import NoChannelsError


def plot_telemetry_channels(
    solution: TelemetrySolution,
    channels: list[DataChannel],
    *,
    title: Optional[str] = None,
):
    """Creates a plot of telemetry channels."""
    if len(channels) == 0:
        raise NoChannelsError

    axs = _create_axs(channels)

    for i, channel in enumerate(channels):
        y_data = channel(solution)
        axs[i].plot(y_data)

    if title is not None:
        plt.suptitle(title)

    plt.show()


def _create_axs(channels: list[TelemetryChannel]) -> list[plt.Axes]:
    """Construct a set of axes for plotting telemetry channels."""
    _, axs = plt.subplots(nrows=len(channels), sharex=True)
    if isinstance(axs, plt.Axes):
        axs = [axs]
    return axs
