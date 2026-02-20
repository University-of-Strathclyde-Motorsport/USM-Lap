"""
This module contains functions for plotting GG and GGV scatter plots.
"""

import matplotlib.pyplot as plt

from usmlap.simulation.channels.library import (
    LateralAcceleration,
    LongitudinalAcceleration,
    Velocity,
)
from usmlap.simulation.solution import Solution


def plot_velocity_acceleration(solution: Solution) -> None:
    """
    Create a scatter plot of velocity and longitudinal acceleration.
    """

    _, ax = plt.subplots()

    velocity = Velocity.get_values(solution)
    longitudinal = LongitudinalAcceleration.get_values(solution)

    ax.scatter(velocity, longitudinal)

    ax.set_xlabel(Velocity.get_label())
    ax.set_ylabel(LongitudinalAcceleration.get_label())
    ax.set_title("Velocity - Acceleration")
    ax.grid()

    plt.show()


def plot_gg(solution: Solution) -> None:
    """
    Create a scatter plot of lateral and longitudinal acceleration.
    """

    _, ax = plt.subplots()

    lateral = LateralAcceleration.get_values(solution)
    longitudinal = LongitudinalAcceleration.get_values(solution)

    ax.scatter(lateral, longitudinal)

    ax.set_xlabel(LateralAcceleration.get_label())
    ax.set_ylabel(LongitudinalAcceleration.get_label())
    ax.set_title("GG Plot")
    ax.grid()

    plt.show()


def plot_ggv(solution: Solution) -> None:
    """
    Create a 3D scatter plot of velocity, lateral and longitudinal acceleration.
    """

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    lateral = LateralAcceleration.get_values(solution)
    longitudinal = LongitudinalAcceleration.get_values(solution)
    velocity = Velocity.get_values(solution)

    ax.scatter(lateral, longitudinal, velocity)

    ax.set_xlabel(LateralAcceleration.get_label())
    ax.set_ylabel(LongitudinalAcceleration.get_label())
    ax.set_zlabel(Velocity.get_label())
    ax.set_title("GG Plot")
    ax.grid()

    plt.show()
