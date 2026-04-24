"""
This module contains code for representing the solution to a simulation.
"""

from __future__ import annotations

import logging
from copy import copy
from dataclasses import dataclass, field
from typing import Generator, Optional

from usmlap.model import (
    CalculatedVehicleState,
    TractionModel,
    TransientVariables,
)
from usmlap.model.vehicle_state import Trajectory
from usmlap.track import Mesh, TrackNode


@dataclass
class SolutionNode(object):
    """
    The solution at a single node.

    Attributes:
        track_node (TrackNode): The corresponding track node.
        maximum_velocity (float): The maximum possible velocity at the node,
            obtained from the lateral vehicle model.
        acceleration (float): The longitudinal acceleration at the node.
        transient_variables (TransientVariables): The transient variables at the node.
        calculated_vehicle_state (CalculatedVehicleState): The state of the vehicle at the node.
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
    transient_variables: TransientVariables = field(
        default_factory=TransientVariables.get_default
    )
    calculated_vehicle_state: Optional[CalculatedVehicleState] = None
    next: Optional[SolutionNode] = None
    previous: Optional[SolutionNode] = None

    @property
    def apex_velocity(self) -> float:
        velocities: list[float] = [self.maximum_velocity]
        if self._initial_velocity_anchored:
            velocities.append(self.initial_velocity)
        if self._final_velocity_anchored:
            velocities.append(self.final_velocity)
        return min(velocities)

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
    def trajectory(self) -> Trajectory:
        return Trajectory(
            curvature=self.track_node.curvature,
            velocity=self.average_velocity,
            ax=self.longitudinal_acceleration,
        )

    @property
    def length(self) -> float:
        return self.track_node.length

    @property
    def sector(self) -> str:
        return self.track_node.sector

    @property
    def lap_number(self) -> int:
        return self.track_node.lap_number

    @property
    def lateral_acceleration(self) -> float:
        return self.average_velocity**2 * self.track_node.curvature

    @property
    def time(self) -> float:
        return self.length / self.average_velocity

    @property
    def energy_used(self) -> float:
        if self.calculated_vehicle_state is None:
            return 0
        return self.calculated_vehicle_state.motor_power * self.time  # TODO

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


@dataclass
class Solution(object):
    """
    The solution to a simulation.
    """

    nodes: list[SolutionNode]
    vehicle_model: TractionModel

    def __post_init__(self) -> None:
        for i in range(len(self.nodes) - 1):
            self.nodes[i].next = self.nodes[i + 1]
            self.nodes[i + 1].previous = self.nodes[i]

    def __iter__(self) -> Generator[SolutionNode]:
        for node in self.nodes:
            yield node

    def __str__(self) -> str:
        return f"Total time: {self.total_time:.3f}s"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def total_time(self) -> float:
        return sum(node.time for node in self)

    @property
    def total_length(self) -> float:
        return sum(node.length for node in self)

    @property
    def total_energy_used(self) -> float:
        return sum(node.energy_used for node in self)

    @property
    def average_velocity(self) -> float:
        return self.total_length / self.total_time

    def get_sector_time(self, sector: str) -> float:
        """
        Get the time for a given sector.

        Args:
            sector (int): The sector to get the time for.

        Returns:
            sector_time (float): The sum of times for the nodes in the sector.
        """
        return sum([node.time for node in self if node.sector == sector])

    def get_sector_boundary_positions(self) -> list[float]:
        """
        Get a list of positions where the sector changes.

        Returns:
            sector_boundary_positions (list[float]): List of positions.
        """
        sector = self.nodes[0].track_node.sector
        positions: list[float] = []
        for node in self.nodes:
            if node.track_node.sector is not sector:
                positions.append(node.track_node.position)
            sector = node.track_node.sector

        return positions

    def get_apex_indices(self) -> list[int]:
        """
        Get a list of apex indices.

        Returns:
            apex_indices (list[int]): Indices of apexes.
        """
        return [i for i, node in enumerate(self.nodes) if node.is_apex()]

    def get_sorted_apex_indices(self) -> list[int]:
        """
        Get a list of apex indices, sorted by maximum velocity from low to high.

        Returns:
            sorted_apex_indices (list[int]): Indices of apexes.
        """
        indices = self.get_apex_indices()
        velocities = [self.nodes[i].apex_velocity for i in indices]
        _, sorted_indices = zip(*sorted(zip(velocities, indices)))
        return list(sorted_indices)

    def get_apexes(self) -> list[SolutionNode]:
        """
        Get a list of apex nodes.

        Returns:
            apexes (list[SolutionNode]): Solution nodes which are apexes.
        """
        return [node for node in self if node.is_apex()]

    def set_apexes(self, apexes: list[int]) -> None:
        for i in apexes:
            self.nodes[i].add_apex()

    def get_subset(self, indices: list[int]) -> Solution:
        """
        Return a new solution containing only the nodes at the given indices.

        Args:
            indices (list[int]):
                The indices of the nodes to include in the new solution.

        Returns:
            new_solution (Solution): The new solution.
        """
        new_solution = copy(self)
        new_solution.nodes = [self.nodes[i] for i in indices]
        return new_solution

    def get_lap_solutions(self) -> list[Solution]:
        """
        Get a list of solutions separated by lap.
        """
        laps = {node.lap_number for node in self.nodes}
        solutions: list[Solution] = []
        for lap in laps:
            indices = [
                i for i, node in enumerate(self.nodes) if node.lap_number == lap
            ]
            solutions.append(self.get_subset(indices))
        return solutions


# TODO: deprecate this
def create_new_solution(
    track_mesh: Mesh,
    vehicle_model: TractionModel,
    initial_state: TransientVariables,
) -> Solution:
    """
    Create a new solution from a track mesh and vehicle model.

    Args:
        track_mesh (Mesh): The track mesh.
        vehicle_model (TractionModel): The vehicle model.

    Returns:
        solution (Solution): A blank solution.
    """
    transient_variables = initialise_transient_variables(
        track_mesh, initial_state
    )
    solution_nodes = [
        SolutionNode(track_node=track_node, transient_variables=estimated_state)
        for track_node, estimated_state in zip(
            track_mesh.nodes, transient_variables
        )
    ]
    solution = Solution(nodes=solution_nodes, vehicle_model=vehicle_model)
    return solution


def initialise_transient_variables(
    track_mesh: Mesh, initial_state: TransientVariables
) -> list[TransientVariables]:
    """
    Generate initial estimated state variables for a simulation.
    """
    return [initial_state for _ in range(track_mesh.node_count)]
