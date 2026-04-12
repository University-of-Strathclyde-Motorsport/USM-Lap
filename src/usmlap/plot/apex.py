"""
This module contains functions for plotting velocity profiles and apexes.
"""

import matplotlib.pyplot as plt

from usmlap.simulation import Solution
from usmlap.simulation.channels.library import (
    MaximumVelocity,
    Position,
    Velocity,
)

from .style import USM_BLUE, USM_LIGHT_BLUE, USM_RED


def plot_apexes(solution: Solution) -> None:
    """
    Plot a velocity profile, with apexes highlighted.
    """

    position = Position.get_values(solution)
    curvature = [node.track_node.curvature for node in solution]
    velocity = Velocity.get_values(solution)
    maximum_velocity = MaximumVelocity.get_values(solution)
    sector_boundary_positions = solution.get_sector_boundary_positions()

    apex_indices = solution.get_sorted_apex_indices()
    apex_solution = solution.get_subset(apex_indices)

    apex_velocity = Velocity.get_values(apex_solution)
    apex_position = Position.get_values(apex_solution)

    fig, (ax_curvature, ax_apex) = plt.subplots(nrows=2, height_ratios=[1, 2])

    ax_curvature.plot(position, curvature, color=USM_BLUE, zorder=2)
    ax_curvature.axhline(0, color="black", linewidth=1, zorder=1)

    for sector_boundary in sector_boundary_positions:
        ax_curvature.axvline(
            sector_boundary, color="black", linewidth=1, linestyle="dashed"
        )

    ax_apex.plot(
        position,
        maximum_velocity,
        color=USM_LIGHT_BLUE,
        label="Maximum velocity",
    )
    ax_apex.plot(position, velocity, color=USM_BLUE, label="Velocity solution")
    ax_apex.scatter(apex_position, apex_velocity, color=USM_RED, label="Apexes")

    for i in range(len(apex_position)):
        plt.text(apex_position[i] + 5, apex_velocity[i], str(i + 1))

    ax_curvature.set_xlim(min(position), max(position))
    a, b = ax_curvature.get_ylim()
    c = max(abs(a), abs(b))
    ax_curvature.set_ylim(-c, c)
    ax_apex.set_xlim(min(position), max(position))

    ax_curvature.set_xlabel(Position.get_label())
    ax_curvature.set_ylabel("Curvature (1/m)")
    ax_apex.set_xlabel(Position.get_label())
    ax_apex.set_ylabel(Velocity.get_label())
    fig.suptitle("Velocity Profile")

    ax_curvature.grid()
    ax_apex.grid()
    ax_apex.legend()
    plt.tight_layout()
    plt.show()
