"""
This module implements a quasi-steady-state solver.
"""

import math
from .solver_interface import SolverInterface
from simulation.model.point_mass import PointMassVehicleModel
from track.mesh import Mesh
from track.mesh import Node as TrackNode
from simulation.solution import Solution
from simulation.solution import Node as SolutionNode


class QuasiSteadyStateSolver(SolverInterface):
    """
    Quasi-steady-state solver.
    """

    vehicle_model: PointMassVehicleModel
    track_mesh: Mesh
    solution: Solution = Solution()

    def __init__(
        self, vehicle_model: PointMassVehicleModel, track_mesh: Mesh
    ) -> None:
        self.vehicle_model = vehicle_model
        self.track_mesh = track_mesh

    def solve(self) -> Solution:
        for node in self.track_mesh.nodes:
            self.solution.append(
                SolutionNode(
                    node=node,
                    maximum_velocity=self.solve_maximum_velocity(node),
                )
            )

        apexes = self.solution.find_apexes()
        apexes.insert(0, 0)
        self.solution[0].initial_velocity = 0

        # Forward propagation
        for apex in apexes:
            if apex != 0:
                self.solution[apex].initial_velocity = self.solution[
                    apex
                ].maximum_velocity

            i = apex
            while i < len(self.solution):
                current_node = self.solution[i]
                final_velocity = self.calculate_final_velocity(current_node)
                current_node.final_velocity = final_velocity

                if i >= len(self.solution) - 1:
                    break

                next_node = self.solution[i + 1]
                next_node.initial_velocity = final_velocity

                if i + 1 in apexes:
                    if final_velocity < next_node.maximum_velocity:
                        apexes.remove(i + 1)
                    else:
                        break

                i += 1

        print(f"There are {len(apexes)} apexes before back propagation")

        # Backward propagation
        for apex in apexes:
            i = apex
            while i > 0:
                current_node = self.solution[i]
                previous_node = self.solution[i - 1]

                maximum_velocity = previous_node.final_velocity
                if maximum_velocity <= current_node.final_velocity:
                    break

                initial_velocity = self.calculate_initial_velocity(
                    current_node, maximum_velocity
                )

                current_node.initial_velocity = initial_velocity
                previous_node.final_velocity = initial_velocity

                if i - 1 in apexes:
                    if initial_velocity < previous_node.final_velocity:
                        apexes.remove(i - 1)
                    else:
                        break

                i -= 1

        print(f"There are {len(apexes)} apexes")
        return self.solution

    def solve_maximum_velocity(self, node: TrackNode) -> float:
        return self.vehicle_model.lateral_vehicle_model(node).velocity

    def calculate_final_velocity(self, node_solution: SolutionNode) -> float:
        maximum_velocity = node_solution.maximum_velocity
        traction_limit_velocity = self.traction_limit_velocity(node_solution)
        return min(traction_limit_velocity, maximum_velocity)

    def calculate_initial_velocity(
        self, node_solution: SolutionNode, maximum_velocity: float
    ) -> float:
        traction_limit_velocity = self.traction_limit_velocity_braking(
            node_solution
        )
        return min(traction_limit_velocity, maximum_velocity)

    def traction_limit_velocity(self, node_solution: SolutionNode) -> float:
        try:
            traction_limited_acceleration = (
                self.vehicle_model.calculate_acceleration(
                    node=node_solution.node,
                    velocity=node_solution.initial_velocity,
                )
            )
            traction_limited_velocity = calculate_next_velocity(
                initial_velocity=node_solution.initial_velocity,
                acceleration=traction_limited_acceleration,
                displacement=node_solution.node.length,
            )
            return traction_limited_velocity
        except ValueError:
            return node_solution.maximum_velocity

    def traction_limit_velocity_braking(
        self, node_solution: SolutionNode
    ) -> float:
        try:
            traction_limited_braking = self.vehicle_model.calculate_braking(
                node=node_solution.node,
                velocity=node_solution.final_velocity,
            )
            traction_limited_velocity = calculate_previous_velocity(
                initial_velocity=node_solution.final_velocity,
                acceleration=traction_limited_braking,
                displacement=node_solution.node.length,
            )
            return traction_limited_velocity
        except ValueError:
            return node_solution.maximum_velocity


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
