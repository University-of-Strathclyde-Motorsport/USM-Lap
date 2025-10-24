"""
This module contains code for representing the solution to a simulation.
"""

from collections import UserList
from pydantic import BaseModel
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from track.mesh import Node


VELOCITY_LABEL = "Velocity (m/s)"
LONGITUDINAL_ACCELERATION_LABEL = "Longitudinal Acceleration (m/s^2)"
LATERAL_ACCELERATION_LABEL = "Lateral Acceleration (m/s^2)"


class NodeSolution(BaseModel):
    """
    The solution at a single node.
    """

    node: Node
    maximum_velocity: float
    forward_velocity: float = 0
    backward_velocity: float = 0
    acceleration: float = 0

    @property
    def velocity(self) -> float:
        return min(self.forward_velocity, self.backward_velocity)

    @property
    def lateral_acceleration(self) -> float:
        return self.velocity**2 * self.node.curvature


class Solution(UserList[NodeSolution]):
    """
    The solution to a simulation.
    """

    @property
    def velocity(self) -> list[float]:
        return [node.velocity for node in self.data]

    @property
    def lateral_acceleration(self) -> list[float]:
        return [node.lateral_acceleration for node in self.data]

    @property
    def longitudinal_acceleration(self) -> list[float]:
        acceleration: list[float] = []
        for i in range(len(self.data) - 1):
            v = self.data[i + 1].velocity
            u = self.data[i].velocity
            s = self.data[i].node.length
            acceleration.append((v**2 - u**2) / (2 * s))
        acceleration.append(acceleration[-1])
        return acceleration

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
        forward_velocity = [solution.forward_velocity for solution in self.data]
        backward_velocity = [
            solution.backward_velocity for solution in self.data
        ]
        velocity = [solution.velocity for solution in self.data]
        apexes = self.find_apexes()
        apex_velocity = [self.data[apex].maximum_velocity for apex in apexes]
        apex_position = [self.data[apex].node.position for apex in apexes]

        fig, ax = plt.subplots()
        fig.suptitle("Solution")
        ax.plot(position, maximum_velocity, color="blue")
        ax.plot(position, forward_velocity, color="green", linestyle="--")
        ax.plot(position, backward_velocity, color="red", linestyle="--")
        ax.plot(position, velocity, color="orange")
        ax.scatter(apex_position, apex_velocity, color="red")
        for i in range(len(apexes)):
            plt.text(apex_position[i] + 5, apex_velocity[i], str(i + 1))
        ax.set_xlabel("Position (m)")
        ax.set_ylabel(VELOCITY_LABEL)
        ax.set_title("Maximum Velocity")
        ax.grid()
        ax.set_xlim(0, 200)
        plt.show()

    def plot_velocity_acceleration(self) -> None:
        fig = plt.figure()
        ax = fig.add_subplot()
        ax.scatter(self.velocity, self.longitudinal_acceleration)
        ax.set_xlabel(VELOCITY_LABEL)
        ax.set_ylabel(LONGITUDINAL_ACCELERATION_LABEL)
        ax.set_title("Velocity - Acceleration")
        ax.grid()
        plt.show()

    def plot_gg(self) -> None:
        fig = plt.figure()
        ax = fig.add_subplot()
        ax.scatter(self.lateral_acceleration, self.longitudinal_acceleration)
        ax.set_xlabel(LATERAL_ACCELERATION_LABEL)
        ax.set_ylabel(LONGITUDINAL_ACCELERATION_LABEL)
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
        ax.set_xlabel(LATERAL_ACCELERATION_LABEL)
        ax.set_ylabel(LONGITUDINAL_ACCELERATION_LABEL)
        ax.set_zlabel(VELOCITY_LABEL)
        ax.set_title("GGV Plot")
        ax.set_ylim(-50, 50)
        ax.grid()
        plt.show()
