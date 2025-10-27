"""
This module contains code for representing the solution to a simulation.
"""

from collections import UserList
from pydantic import BaseModel
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from track.mesh import Node as TrackNode


LABELS = {
    "velocity": "Velocity (m/s)",
    "longitudinal_acceleration": "Longitudinal Acceleration (m/s^2)",
    "lateral_acceleration": "Lateral Acceleration (m/s^2)",
}


class Node(BaseModel):
    """
    The solution at a single node.
    """

    node: TrackNode
    maximum_velocity: float
    acceleration: float = 0
    initial_velocity: float = 0
    final_velocity: float = 0
    anchor: bool = False

    @property
    def length(self) -> float:
        return self.node.length

    @property
    def velocity(self) -> float:
        return (self.initial_velocity + self.final_velocity) / 2

    @property
    def longitudinal_acceleration(self) -> float:
        return (self.final_velocity**2 - self.initial_velocity**2) / (
            2 * self.length
        )

    @property
    def lateral_acceleration(self) -> float:
        return self.velocity**2 * self.node.curvature

    @property
    def time(self) -> float:
        return self.length / self.velocity


class Solution(UserList[Node]):
    """
    The solution to a simulation.
    """

    @property
    def velocity(self) -> list[float]:
        return [node.velocity for node in self.data]

    @property
    def initial_velocity(self) -> list[float]:
        return [node.initial_velocity for node in self.data]

    @property
    def lateral_acceleration(self) -> list[float]:
        return [node.lateral_acceleration for node in self.data]

    @property
    def longitudinal_acceleration(self) -> list[float]:
        return [node.longitudinal_acceleration for node in self.data]

    @property
    def total_time(self) -> float:
        return sum(node.time for node in self.data)

    @property
    def total_length(self) -> float:
        return sum(node.length for node in self.data)

    @property
    def average_velocity(self) -> float:
        return self.total_length / self.total_time

    def find_apexes(self) -> list[int]:
        apex_indices, _ = find_peaks(
            [-node.maximum_velocity for node in self.data]
        )
        apex_indices = set(apex_indices.tolist())
        apex_indices.update([0, len(self.data) - 1])
        apex_velocities = [self.data[i].maximum_velocity for i in apex_indices]
        _, sorted_apexes = zip(*sorted(zip(apex_velocities, apex_indices)))
        return list(sorted_apexes)

    def plot_apexes(self) -> None:
        position = [solution.node.position for solution in self.data]
        maximum_velocity = [solution.maximum_velocity for solution in self.data]
        apexes = self.find_apexes()
        apex_velocity = [self.data[apex].maximum_velocity for apex in apexes]
        apex_position = [self.data[apex].node.position for apex in apexes]

        fig, ax = plt.subplots()
        fig.suptitle("Solution")
        ax.plot(position, maximum_velocity, color="blue")
        ax.plot(position, self.velocity, color="orange")
        ax.scatter(apex_position, apex_velocity, color="red")
        for i in range(len(apexes)):
            plt.text(apex_position[i] + 5, apex_velocity[i], str(i + 1))
        ax.set_xlabel("Position (m)")
        ax.set_ylabel(LABELS["velocity"])
        ax.set_title("Maximum Velocity")
        ax.grid()
        plt.show()

    def plot_velocity_acceleration(self) -> None:
        fig = plt.figure()
        ax = fig.add_subplot()
        ax.scatter(self.velocity, self.longitudinal_acceleration)
        ax.set_xlabel(LABELS["velocity"])
        ax.set_ylabel(LABELS["longitudinal_acceleration"])
        ax.set_title("Velocity - Acceleration")
        ax.grid()
        plt.show()

    def plot_gg(self) -> None:
        fig = plt.figure()
        ax = fig.add_subplot()
        ax.scatter(self.lateral_acceleration, self.longitudinal_acceleration)
        ax.set_xlabel(LABELS["lateral_acceleration"])
        ax.set_ylabel(LABELS["longitudinal_acceleration"])
        ax.set_title("GG Plot")
        ax.grid()
        plt.show()

    def plot_ggv(self) -> None:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(
            self.lateral_acceleration,
            self.longitudinal_acceleration,
            self.velocity,
        )
        ax.set_xlabel(LABELS["lateral_acceleration"])
        ax.set_ylabel(LABELS["longitudinal_acceleration"])
        ax.set_zlabel(LABELS["velocity"])
        ax.set_title("GGV Plot")
        ax.set_ylim(-50, 50)
        ax.grid()
        plt.show()
