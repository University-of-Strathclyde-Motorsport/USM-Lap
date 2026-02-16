"""
This module contains functions for plotting simulation results.
"""

import matplotlib.pyplot as plt

from simulation.solution import Solution

LABELS = {
    "velocity": "Velocity (m/s)",
    "longitudinal_acceleration": "Longitudinal Acceleration (m/s^2)",
    "lateral_acceleration": "Lateral Acceleration (m/s^2)",
}


def plot_velocity_acceleration(solution: Solution) -> None:
    """
    Create a scatter plot of velocity and longitudinal acceleration.
    """

    fig = plt.figure()
    ax = fig.add_subplot()
    ax.scatter(solution.velocity, solution.longitudinal_acceleration)
    ax.set_xlabel(LABELS["velocity"])
    ax.set_ylabel(LABELS["longitudinal_acceleration"])
    ax.set_title("Velocity - Acceleration")
    ax.grid()
    plt.show()


def plot_gg(solution: Solution) -> None:
    """
    Create a scatter plot of lateral and longitudinal acceleration.
    """
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.scatter(
        solution.lateral_acceleration, solution.longitudinal_acceleration
    )
    ax.set_xlabel(LABELS["lateral_acceleration"])
    ax.set_ylabel(LABELS["longitudinal_acceleration"])
    ax.set_title("GG Plot")
    ax.grid()
    plt.show()


def plot_ggv(solution: Solution) -> None:
    """
    Create a 3D scatter plot of velocity, lateral and longitudinal acceleration.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")  # type: ignore
    ax.scatter(
        solution.lateral_acceleration,
        solution.longitudinal_acceleration,
        solution.velocity,
    )
    ax.set_xlabel(LABELS["lateral_acceleration"])
    ax.set_ylabel(LABELS["longitudinal_acceleration"])
    ax.set_zlabel(LABELS["velocity"])
    ax.set_title("GGV Plot")
    ax.set_ylim(-50, 50)
    ax.grid()
    plt.show()
