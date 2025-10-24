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
from .solution import Solution, NodeSolution


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

        # Forward propagation
        for apex in apexes:
            print(f"Forwards propagating from apex at node {apex}")
            self.solution[apex].forward_velocity = self.solution[
                apex
            ].maximum_velocity

            i = apex
            while i < len(self.solution) - 1:
                maximum_velocity = self.solution[i + 1].maximum_velocity
                if maximum_velocity <= self.solution[i].forward_velocity:
                    velocity = self.solution[i + 1].maximum_velocity
                else:
                    traction_limited_velocity = (
                        self.calculate_traction_limited_velocity(
                            node_solution=self.solution[i]
                        )
                    )
                    velocity = min(traction_limited_velocity, maximum_velocity)

                self.solution[i + 1].forward_velocity = velocity
                i += 1
                if i in apexes:
                    if (
                        self.solution[i].forward_velocity
                        < self.solution[i].maximum_velocity
                    ):
                        apexes.remove(i)
                    else:
                        break

        # Backward propagation
        for apex in apexes:
            print(f"Backwards propagating from apex at node {apex}")
            self.solution[apex].backward_velocity = self.solution[
                apex
            ].maximum_velocity

            i = apex
            while i > 0:
                maximum_velocity = self.solution[i - 1].maximum_velocity
                if maximum_velocity <= self.solution[i].backward_velocity:
                    velocity = self.solution[i - 1].maximum_velocity
                else:
                    traction_limited_velocity = (
                        self.calculate_traction_limited_velocity_braking(
                            node_solution=self.solution[i]
                        )
                    )
                    velocity = min(traction_limited_velocity, maximum_velocity)

                self.solution[i - 1].backward_velocity = velocity
                i -= 1
                if i in apexes:
                    if (
                        self.solution[i].backward_velocity
                        < self.solution[i].maximum_velocity
                    ):
                        apexes.remove(i)
                    else:
                        break

        print(f"There are {len(apexes)} apexes")
        return self.solution

    def solve_maximum_velocity(self, node: Node) -> float:
        if node.curvature == 0:
            return self.vehicle.maximum_velocity
        return self.vehicle_model.lateral_vehicle_model(
            self.vehicle, self.environment, node
        ).velocity

    def calculate_traction_limited_velocity(
        self, node_solution: NodeSolution
    ) -> float:
        traction_limited_acceleration = (
            self.vehicle_model.calculate_acceleration(
                vehicle=self.vehicle,
                environment=self.environment,
                node=node_solution.node,
                velocity=node_solution.forward_velocity,
            )
        )
        traction_limited_velocity = calculate_next_velocity(
            initial_velocity=node_solution.forward_velocity,
            acceleration=traction_limited_acceleration,
            displacement=node_solution.node.length,
        )
        return traction_limited_velocity

    def calculate_traction_limited_velocity_braking(
        self, node_solution: NodeSolution
    ) -> float:
        traction_limited_braking = self.vehicle_model.calculate_braking(
            vehicle=self.vehicle,
            environment=self.environment,
            node=node_solution.node,
            velocity=node_solution.backward_velocity,
        )
        traction_limited_velocity = calculate_previous_velocity(
            initial_velocity=node_solution.backward_velocity,
            acceleration=traction_limited_braking,
            displacement=node_solution.node.length,
        )
        return traction_limited_velocity


def calculate_next_velocity(
    initial_velocity: float, acceleration: float, displacement: float
) -> float:
    return math.sqrt(initial_velocity**2 + 2 * acceleration * displacement)


def calculate_previous_velocity(
    initial_velocity: float, acceleration: float, displacement: float
) -> float:
    term = initial_velocity**2 + 2 * acceleration * displacement
    if term <= 0:
        return 0
    else:
        return math.sqrt(term)
