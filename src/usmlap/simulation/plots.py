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


def plot_apexes(solution: Solution) -> None:
    """
    Plot a velocity profile, with apexes highlighted.
    """
    position = [node.track_node.position for node in solution.nodes]
    maximum_velocity = [node.maximum_velocity for node in solution.nodes]
    apexes = solution.get_apexes()
    apex_velocity = [apex.maximum_velocity for apex in apexes]
    apex_position = [apex.track_node.position for apex in apexes]

    fig, ax = plt.subplots()
    fig.suptitle("Solution")
    ax.plot(position, maximum_velocity, color="lightblue")
    ax.plot(position, solution.velocity, color="blue")
    ax.scatter(apex_position, apex_velocity, color="red")
    for i in range(len(apexes)):
        plt.text(apex_position[i] + 5, apex_velocity[i], str(i + 1))
    ax.set_xlabel("Position (m)")
    ax.set_ylabel(LABELS["velocity"])
    ax.set_title("Maximum Velocity")
    ax.grid()
    plt.show()


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
