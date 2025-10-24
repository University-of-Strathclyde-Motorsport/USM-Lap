"""
This module contains code for running a simulation.
"""

from __future__ import annotations
import math
from pydantic import BaseModel, ConfigDict
from vehicle.vehicle import Vehicle
from track.mesh import Mesh, Node
from .environment import Environment
from .model.point_mass import PointMassVehicleModel
from .solver.quasi_steady_state import QuasiSteadyStateSolver
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from collections import UserList


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


class Solution(UserList[NodeSolution]):
    """
    The solution to a simulation.
    """

    def find_apexes(self) -> list[int]:
        apex_indices, _ = find_peaks(
            [-solution.maximum_velocity for solution in self.data]
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
        ax.scatter(apex_position, apex_velocity, marker="o", color="red")
        for i in range(len(apexes)):
            plt.text(apex_position[i] + 2, apex_velocity[i], str(i + 1))
        ax.set_xlabel("Position (m)")
        ax.set_ylabel("Velocity (m/s)")
        ax.set_title("Maximum Velocity")
        ax.grid()
        plt.show()


class Simulation(BaseModel):
    """
    A simulation object.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    vehicle: Vehicle
    track: Mesh
    environment: Environment = Environment()
    vehicle_model: PointMassVehicleModel = PointMassVehicleModel()
    solver: QuasiSteadyStateSolver = QuasiSteadyStateSolver()
    solution: Solution = Solution()

    def solve(self) -> Solution:
        for node in self.track.nodes:
            self.solution.append(
                NodeSolution(
                    node=node,
                    maximum_velocity=self.solve_maximum_velocity(node),
                )
            )
        self.solution[0].maximum_velocity = 0
        apexes = self.solution.find_apexes()
        print(f"Apexes: {apexes}")

        # Forward propagation
        for apex in apexes:
            print(f"Forwards propagating from apex at node {apex}")
            self.solution[apex].forward_velocity = self.solution[
                apex
            ].maximum_velocity

            i = apex
            while i < len(self.solution) - 1:
                if (
                    self.solution[i + 1].maximum_velocity
                    <= self.solution[i].forward_velocity
                ):
                    next_velocity = self.solution[i + 1].maximum_velocity
                else:
                    potential_acceleration = (
                        self.vehicle_model.calculate_acceleration(
                            vehicle=self.vehicle,
                            environment=self.environment,
                            node=self.solution[i].node,
                            velocity=self.solution[i].forward_velocity,
                        )
                    )
                    u = self.solution[i].forward_velocity
                    s = self.solution[i].node.length
                    potential_velocity = math.sqrt(
                        u**2 + 2 * potential_acceleration * s
                    )
                    next_velocity = min(
                        potential_velocity,
                        self.solution[i + 1].maximum_velocity,
                    )

                self.solution[i + 1].forward_velocity = next_velocity
                i += 1
                if i in apexes:
                    if (
                        self.solution[i].forward_velocity
                        < self.solution[i].maximum_velocity
                    ):
                        apexes.remove(i)
                    else:
                        break
                print(
                    f"Node: {i}, maximum velocity: {self.solution[i].maximum_velocity}, velocity: {next_velocity}"
                )

        # Backward propagation
        for apex in apexes:
            print(f"Backwards propagating from apex at node {apex}")
            self.solution[apex].backward_velocity = self.solution[
                apex
            ].maximum_velocity

            i = apex
            while i > 0:
                if (
                    self.solution[i - 1].maximum_velocity
                    <= self.solution[i].forward_velocity
                ):
                    next_velocity = self.solution[i - 1].maximum_velocity
                else:
                    potential_acceleration = (
                        self.vehicle_model.calculate_braking(
                            vehicle=self.vehicle,
                            environment=self.environment,
                            node=self.solution[i].node,
                            velocity=self.solution[i].backward_velocity,
                        )
                    )
                    v = self.solution[i].backward_velocity
                    s = self.solution[i].node.length
                    term = v**2 + 2 * potential_acceleration * s
                    if term <= 0:
                        potential_velocity = 0
                    else:
                        potential_velocity = math.sqrt(term)

                    next_velocity = min(
                        potential_velocity,
                        self.solution[i - 1].maximum_velocity,
                    )

                self.solution[i - 1].backward_velocity = next_velocity
                i -= 1
                if i in apexes:
                    if (
                        self.solution[i].backward_velocity
                        < self.solution[i].maximum_velocity
                    ):
                        apexes.remove(i)
                    else:
                        break
                print(
                    f"Node: {i}, maximum velocity: {self.solution[i].maximum_velocity}, velocity: {next_velocity}"
                )

        print(f"There are {len(apexes)} apexes")
        return self.solution

    def solve_maximum_velocity(self, node: Node) -> float:
        if node.curvature == 0:
            return self.vehicle.maximum_velocity
        return self.vehicle_model.lateral_vehicle_model(
            self.vehicle, self.environment, node
        ).velocity
