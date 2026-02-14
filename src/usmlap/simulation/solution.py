"""
This module contains code for representing the solution to a simulation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from simulation.model.vehicle_model import VehicleModelInterface
from simulation.vehicle_state import FullVehicleState, StateVariables
from track.mesh import Mesh, TrackNode


@dataclass
class SolutionNode(object):
    """
    The solution at a single node.

    Attributes:
        track_node (TrackNode): The corresponding track node.
        maximum_velocity (float): The maximum possible velocity at the node,
            obtained from the lateral vehicle model.
        acceleration (float): The longitudinal acceleration at the node.
        state_variables (StateVariables): The state variables at the node.
        vehicle_state (FullVehicleState): The state of the vehicle at the node.
        next (Optional[SolutionNode]): The next node in the solution
            (`None` if this is the final node).
        previous (Optional[SolutionNode]): The previous node in the solution
            (`None` if this is the first node).
        length (float): The length of the track segment.
        initial_velocity (float): The velocity at the start of the node.
        final_velocity (float): The velocity at the end of the node.
        average_velocity (float): The average velocity for the node.
        longitudinal_acceleration (float):
            The longitudinal acceleration for the node.
        lateral_acceleration (float): The lateral acceleration for the node.
        time (float): The time taken to drive this node.
        energy_used (float): The energy used to drive this node.
    """

    track_node: TrackNode
    maximum_velocity: float = 0
    _apex: bool = False
    _initial_velocity: float = 0
    _final_velocity: float = 0
    _initial_velocity_anchored: bool = False
    _final_velocity_anchored: bool = False
    acceleration: float = 0
    state_variables: StateVariables = field(
        default_factory=StateVariables.get_default
    )
    vehicle_state: FullVehicleState = field(
        default_factory=FullVehicleState.get_empty
    )
    next: Optional[SolutionNode] = None
    previous: Optional[SolutionNode] = None

    @property
    def length(self) -> float:
        return self.track_node.length

    @property
    def initial_velocity(self) -> float:
        return self._initial_velocity

    @property
    def final_velocity(self) -> float:
        return self._final_velocity

    @property
    def average_velocity(self) -> float:
        return (self.initial_velocity + self.final_velocity) / 2

    @property
    def longitudinal_acceleration(self) -> float:
        return (self.final_velocity**2 - self.initial_velocity**2) / (
            2 * self.length
        )

    @property
    def lateral_acceleration(self) -> float:
        return self.average_velocity**2 * self.track_node.curvature

    @property
    def time(self) -> float:
        return self.length / self.average_velocity

    @property
    def energy_used(self) -> float:
        return self.vehicle_state.accumulator_power * self.time

    def is_apex(self) -> bool:
        """
        Check if the node is an apex.

        Returns:
            is_apex (bool): `True` is the node is an apex, otherwise `False`.
        """
        return self._apex

    def add_apex(self) -> None:
        """
        Add the node as an apex.
        """
        self._apex = True

    def remove_apex(self) -> None:
        """
        Remove the node as an apex.
        """
        logging.debug("Removing apex")
        self._apex = False

    def evaluate_vehicle_state(
        self, vehicle_model: VehicleModelInterface
    ) -> None:
        """
        Evaluate the full state of the vehicle at this node.

        Args:
            vehicle_model (VehicleModelInterface): The vehicle model to use.
        """
        self.vehicle_state = vehicle_model.resolve_vehicle_state(
            self.state_variables, self.track_node, self.average_velocity
        )

    def set_initial_velocity(self, velocity: float) -> None:
        """
        Set the velocity at the start of the node.
        If the initial velocity has been anchored, it will not be modified.

        Args:
            velocity (float): The initial velocity to be set.
        """
        if not self._initial_velocity_anchored:
            self._initial_velocity = velocity

    def set_final_velocity(self, velocity: float) -> None:
        """
        Set the velocity at the end of the node.
        If the final velocity has been anchored, it will not be modified.

        Args:
            velocity (float): The final velocity to be set.
        """
        if not self._final_velocity_anchored:
            self._final_velocity = velocity

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

    def update_state_variables(self, state_variables: StateVariables) -> None:
        self.state_variables = state_variables


@dataclass
class Solution(object):
    """
    The solution to a simulation.
    """

    nodes: list[SolutionNode]
    vehicle_model: VehicleModelInterface

    def __post_init__(self) -> None:
        for i in range(len(self.nodes) - 1):
            self.nodes[i].next = self.nodes[i + 1]
            self.nodes[i + 1].previous = self.nodes[i]

    @property
    def velocity(self) -> list[float]:
        return [node.average_velocity for node in self.nodes]

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

    def get_sorted_apex_indices(self) -> list[int]:
        """
        Get a list of apex indices, sorted by maximum velocity from low to high.

        Returns:
            sorted_apex_indices (list[int]): Indices of apexes.
        """
        indices = [i for i, node in enumerate(self.nodes) if node.is_apex()]
        velocities = [self.nodes[i].maximum_velocity for i in indices]
        _, sorted_indices = zip(*sorted(zip(velocities, indices)))
        return list(sorted_indices)

    def get_apexes(self) -> list[SolutionNode]:
        """
        Get a list of apex nodes.

        Returns:
            apexes (list[SolutionNode]): Solution nodes which are apexes.
        """
        return [node for node in self.nodes if node.is_apex()]

    def set_apexes(self, apexes: list[int]) -> None:
        for i in apexes:
            self.nodes[i].add_apex()


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
