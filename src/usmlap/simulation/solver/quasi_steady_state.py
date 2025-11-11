"""
This module implements a quasi-steady-state solver.
"""

import math
import logging
from simulation.model.vehicle_model import VehicleState
from .solver_interface import SolverInterface
from track.mesh import Node as TrackNode
from simulation.solution import Solution
from simulation.solution import Node as SolutionNode


class QuasiSteadyStateSolver(SolverInterface):
    """
    Quasi-steady-state solver.
    """

    def solve(self) -> Solution:
        self.solution = Solution()
        logging.info("Solving maximum velocity...")
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

        logging.info("Solving forward propagation...")
        for apex in apexes:
            if apex != 0:
                maximum_velocity = self.solution[apex].maximum_velocity
                self.solution[apex].initial_velocity = maximum_velocity

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

        logging.info("Solving backward propagation...")
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
            vehicle_state = VehicleState(
                velocity=node_solution.initial_velocity
            )
            traction_limited_acceleration = (
                self.vehicle_model.calculate_acceleration(
                    node=node_solution.node,
                    vehicle_state=vehicle_state,
                )
            )
            traction_limited_velocity = calculate_next_velocity(
                initial_velocity=node_solution.initial_velocity,
                acceleration=traction_limited_acceleration,
                displacement=node_solution.node.length,
            )
            return traction_limited_velocity
        except ValueError:
            return node_solution.initial_velocity  # TODO

    def traction_limit_velocity_braking(
        self, node_solution: SolutionNode
    ) -> float:
        try:
            vehicle_state = VehicleState(velocity=node_solution.final_velocity)
            traction_limited_decceleration = (
                self.vehicle_model.calculate_decceleration(
                    node=node_solution.node, vehicle_state=vehicle_state
                )
            )
            traction_limited_velocity = calculate_previous_velocity(
                final_velocity=node_solution.final_velocity,
                decceleration=traction_limited_decceleration,
                displacement=node_solution.node.length,
            )
            return traction_limited_velocity
        except ValueError:
            return node_solution.final_velocity  # TODO


def calculate_next_velocity(
    initial_velocity: float, acceleration: float, displacement: float
) -> float:
    return math.sqrt(initial_velocity**2 + 2 * acceleration * displacement)


def calculate_previous_velocity(
    final_velocity: float, decceleration: float, displacement: float
) -> float:
    term = final_velocity**2 + 2 * decceleration * displacement
    if term <= 0:
        return 0
    else:
        return math.sqrt(term)
