"""
This module contains functions for plotting GG and GGV scatter plots.
"""

from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

from usmlap.plot.style import COLOURMAP, USM_BLUE
from usmlap.telemetry import DataChannel, TelemetrySolution
from usmlap.telemetry.channel.library import (
    LateralAcceleration,
    LongitudinalAcceleration,
    Velocity,
)

VELOCITY: DataChannel = Velocity()
LATERAL_ACCELERATION: DataChannel = LateralAcceleration()
LONGITUDINAL_ACCELERATION: DataChannel = LongitudinalAcceleration()


def plot_velocity_acceleration(solution: TelemetrySolution) -> None:
    """
    Create a scatter plot of velocity and longitudinal acceleration.
    """

    _, ax = plt.subplots()

    ax.scatter(
        VELOCITY(solution),
        LONGITUDINAL_ACCELERATION(solution),
        color=USM_BLUE,
        alpha=0.5,
    )

    ax.set_xlabel(VELOCITY.label_with_unit())
    ax.set_ylabel(LONGITUDINAL_ACCELERATION.label_with_unit())
    ax.set_title("Velocity - Acceleration")
    ax.grid()

    plt.tight_layout()
    plt.show()


def plot_gg(
    solutions: dict[str, TelemetrySolution],
    *,
    title: str = "GG Plot",
    marker_size: float = 30,
    colours: Optional[list[str]] = None,
    show_legend: Optional[bool] = None,
    velocity_transparency: bool = True,
) -> None:
    """
    Create a scatter plot of lateral and longitudinal acceleration.
    """

    if colours is None:
        colourmap = COLOURMAP
    else:
        colourmap = iter(colours)

    if show_legend is None:
        show_legend = len(solutions) > 1

    _, ax = plt.subplots()

    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(0, color="black", linewidth=1)

    for label, solution in solutions.items():
        if velocity_transparency:
            velocity = VELOCITY(solution)
            transparency = np.power(np.array(velocity) / max(velocity), 2)
        else:
            transparency = 1
        ax.scatter(
            LATERAL_ACCELERATION(solution),
            LONGITUDINAL_ACCELERATION(solution),
            color=next(colourmap),
            s=marker_size,
            label=label,
            alpha=transparency,
            linewidths=0,
        )

    if show_legend:
        legend = ax.legend(fontsize=16)
        for lh in legend.legend_handles:  # ty: ignore[unresolved-attribute]
            alphas = np.repeat(1, len(solutions))
            lh.set_alpha(alphas)

    ax.set_xlabel(LATERAL_ACCELERATION.label_with_unit(), fontsize=16)
    ax.set_ylabel(LONGITUDINAL_ACCELERATION.label_with_unit(), fontsize=16)
    ax.set_title(title, fontsize=20)
    ax.tick_params(axis="both", which="major", labelsize=16)
    ax.grid()

    plt.tight_layout()
    plt.show()


def plot_ggv(
    solutions: dict[str, TelemetrySolution],
    *,
    title: str = "GGV Plot",
    marker_size: float = 10,
    colours: Optional[list[str]] = None,
    show_legend: Optional[bool] = None,
) -> None:
    """
    Create a 3D scatter plot of velocity, lateral and longitudinal acceleration.
    """

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    if colours is None:
        colourmap = COLOURMAP
    else:
        colourmap = iter(colours)

    if show_legend is None:
        show_legend = len(solutions) > 1

    for label, solution in solutions.items():
        ax.scatter(
            LATERAL_ACCELERATION(solution),
            LONGITUDINAL_ACCELERATION(solution),
            VELOCITY(solution),
            color=next(colourmap),
            s=marker_size,
            label=label,
        )

    ax.set_xlabel(LATERAL_ACCELERATION.label_with_unit())
    ax.set_ylabel(LONGITUDINAL_ACCELERATION.label_with_unit())
    ax.set_zlabel(VELOCITY.label_with_unit())
    ax.set_title(title)
    ax.grid()

    if show_legend:
        ax.legend()

    plt.tight_layout()
    plt.show()
