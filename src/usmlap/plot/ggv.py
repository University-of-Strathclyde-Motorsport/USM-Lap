"""
This module contains functions for plotting GG and GGV scatter plots.
"""

from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

from usmlap.plot.style import COLOURMAP, USM_BLUE
from usmlap.simulation.channels.library import (
    LateralAcceleration,
    LongitudinalAcceleration,
    Velocity,
)
from usmlap.solver import Solution


def plot_velocity_acceleration(solution: Solution) -> None:
    """
    Create a scatter plot of velocity and longitudinal acceleration.
    """

    _, ax = plt.subplots()

    velocity = Velocity().get_values(solution)
    longitudinal = LongitudinalAcceleration().get_values(solution)

    ax.scatter(velocity, longitudinal, color=USM_BLUE, alpha=0.5)

    ax.set_xlabel(Velocity.get_label())
    ax.set_ylabel(LongitudinalAcceleration.get_label())
    ax.set_title("Velocity - Acceleration")
    ax.grid()

    plt.tight_layout()
    plt.show()


def plot_gg(
    solutions: dict[str, Solution],
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
        lateral = LateralAcceleration().get_values(solution)
        longitudinal = LongitudinalAcceleration().get_values(solution)
        if velocity_transparency:
            velocity = Velocity().get_values(solution)
            transparency = np.power(np.array(velocity) / max(velocity), 2)
        else:
            transparency = 1
        ax.scatter(
            lateral,
            longitudinal,
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

    ax.set_xlabel(LateralAcceleration.get_label(), fontsize=16)
    ax.set_ylabel(LongitudinalAcceleration.get_label(), fontsize=16)
    ax.set_title(title, fontsize=20)
    ax.tick_params(axis="both", which="major", labelsize=16)
    ax.grid()

    plt.tight_layout()
    plt.show()


def plot_ggv(
    solutions: dict[str, Solution],
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
        lateral = LateralAcceleration().get_values(solution)
        longitudinal = LongitudinalAcceleration().get_values(solution)
        velocity = Velocity().get_values(solution)
        ax.scatter(
            lateral, longitudinal, velocity, color=next(colourmap), label=label
        )

    ax.set_xlabel(LateralAcceleration.get_label())
    ax.set_ylabel(LongitudinalAcceleration.get_label())
    ax.set_zlabel(Velocity.get_label())
    ax.set_title(title)
    ax.grid()

    if show_legend:
        ax.legend()

    plt.tight_layout()
    plt.show()
