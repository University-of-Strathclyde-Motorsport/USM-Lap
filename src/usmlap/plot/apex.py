"""
This module contains functions for plotting velocity profiles and apexes.
"""

import matplotlib.pyplot as plt

from simulation.channels.library import MaximumVelocity, Position, Velocity
from simulation.solution import Solution


def plot_apexes(solution: Solution) -> None:
    """
    Plot a velocity profile, with apexes highlighted.
    """

    position = Position.get_values(solution)
    velocity = Velocity.get_values(solution)
    maximum_velocity = MaximumVelocity.get_values(solution)

    apex_indices = solution.get_sorted_apex_indices()
    apex_solution = solution.get_subset(apex_indices)

    apex_velocity = Velocity.get_values(apex_solution)
    apex_position = Position.get_values(apex_solution)

    fig, ax = plt.subplots()
    fig.suptitle("Solution")

    ax.plot(position, maximum_velocity, color="lightblue")
    ax.plot(position, velocity, color="blue")
    ax.scatter(apex_position, apex_velocity, color="red")

    for i in range(len(apex_position)):
        plt.text(apex_position[i] + 5, apex_velocity[i], str(i + 1))

    ax.set_xlabel(Position.get_label())
    ax.set_ylabel(Velocity.get_label())
    ax.set_title("Maximum Velocity")
    ax.grid()

    plt.show()
