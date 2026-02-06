"""
This module contains code for representing the solution to a simulation.
"""

from dataclasses import dataclass, field

from simulation.model.vehicle_model import VehicleModelInterface
from simulation.vehicle_state import FullVehicleState, StateVariables
from track.mesh import Mesh, TrackNode

LABELS = {
    "velocity": "Velocity (m/s)",
    "longitudinal_acceleration": "Longitudinal Acceleration (m/s^2)",
    "lateral_acceleration": "Lateral Acceleration (m/s^2)",
}


def default_state_variables() -> StateVariables:
    """
    Get a blank vehicle state.
    """
    return StateVariables(velocity=0)


@dataclass
class SolutionNode(object):
    """
    The solution at a single node.
    """

    track_node: TrackNode
    maximum_velocity: float = 0
    acceleration: float = 0
    initial_state: StateVariables = field(
        default_factory=default_state_variables
    )
    final_state: StateVariables = field(default_factory=default_state_variables)
    vehicle_state: FullVehicleState = field(
        default_factory=FullVehicleState.get_empty
    )
    _initial_velocity_anchored: bool = False
    _final_velocity_anchored: bool = False

    @property
    def length(self) -> float:
        return self.track_node.length

    @property
    def initial_velocity(self) -> float:
        return self.initial_state.velocity

    @property
    def final_velocity(self) -> float:
        return self.final_state.velocity

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
        return self.velocity**2 * self.track_node.curvature

    @property
    def time(self) -> float:
        return self.length / self.velocity

    @property
    def state_variables(self) -> StateVariables:
        return StateVariables(velocity=self.velocity, ax=self.acceleration)

    def evaluate_vehicle_state(
        self, vehicle_model: VehicleModelInterface
    ) -> None:
        self.vehicle_state = vehicle_model.resolve_vehicle_state(
            self.state_variables, self.track_node
        )

    def set_initial_velocity(self, velocity: float) -> None:
        """
        Set the velocity at the start of the node.
        If the initial velocity has been anchored, it will not be modified.

        Args:
            velocity (float): The initial velocity to be set.
        """
        if not self._initial_velocity_anchored:
            self.initial_state.velocity = velocity

    def set_final_velocity(self, velocity: float) -> None:
        """
        Set the velocity at the end of the node.
        If the final velocity has been anchored, it will not be modified.

        Args:
            velocity (float): The final velocity to be set.
        """
        if not self._final_velocity_anchored:
            self.final_state.velocity = velocity

    def anchor_initial_velocity(self, velocity: float) -> None:
        """
        Anchor the initial velocity of this node.
        It can no longer be modified.

        Args:
            velocity (float): The initial velocity to be set.
        """
        self.set_initial_velocity(velocity)
        self._initial_velocity_anchored = True

    def anchor_final_velocity(self, velocity: float) -> None:
        """
        Anchor the final velocity of this node.
        It can no longer be modified.

        Args:
            velocity (float): The final velocity to be set.
        """
        self.set_final_velocity(velocity)
        self._final_velocity_anchored = True


@dataclass
class Solution(object):
    """
    The solution to a simulation.
    """

    nodes: list[SolutionNode]
    vehicle_model: VehicleModelInterface
    apexes: list[int] = field(default_factory=list[int])

    @property
    def velocity(self) -> list[float]:
        return [node.velocity for node in self.nodes]

    @property
    def initial_velocity(self) -> list[float]:
        return [node.initial_velocity for node in self.nodes]

    @property
    def lateral_acceleration(self) -> list[float]:
        return [node.lateral_acceleration for node in self.nodes]

    @property
    def longitudinal_acceleration(self) -> list[float]:
        return [node.longitudinal_acceleration for node in self.nodes]

    @property
    def total_time(self) -> float:
        return sum(node.time for node in self.nodes)

    @property
    def total_length(self) -> float:
        return sum(node.length for node in self.nodes)

    @property
    def average_velocity(self) -> float:
        return self.total_length / self.total_time

    def evaluate_full_vehicle_state(
        self, vehicle_model: VehicleModelInterface
    ) -> None:
        for node in self.nodes:
            node.evaluate_vehicle_state(vehicle_model)


def create_new_solution(
    track_mesh: Mesh, vehicle_model: VehicleModelInterface
) -> Solution:
    """
    Create a new solution from a track mesh and vehicle model.

    Args:
        track_mesh (Mesh): The track mesh.
        vehicle_model (VehicleModelInterface): The vehicle model.

    Returns:
        solution (Solution): A blank solution.
    """
    solution_nodes = [
        SolutionNode(track_node=track_node) for track_node in track_mesh.nodes
    ]
    solution = Solution(nodes=solution_nodes, vehicle_model=vehicle_model)
    return solution
