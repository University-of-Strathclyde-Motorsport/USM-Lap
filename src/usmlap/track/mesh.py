"""
This module defines nodes and meshes for a track.
"""

from __future__ import annotations

import copy
import math
from dataclasses import dataclass
from typing import Generator

import matplotlib.pyplot as plt
from pydantic import BaseModel, Field

from .track_data import Configuration


class TrackNode(BaseModel):
    """
    A node of a track.

    Attributes:
        Position (float): The position of the node from the start of the track.
        Length (float): The length of the track section.
        Curvature (float): The curvature of the track section (left +ve).
        Elevation (float): The elevation of the track section.
        Inclination (float): The inclination angle of the track section.
        Banking (float): The banking angle of the track section (+ve slope right to left).
        GripFactor (float): The grip factor of the track section.
        Sector (int): The sector of the track section.
    """

    position: float = Field(ge=0)
    length: float = Field(gt=0)
    curvature: float
    elevation: float
    inclination: float = Field(gt=-math.pi / 2, lt=math.pi / 2, default=0)
    banking: float = Field(ge=-math.pi / 2, le=math.pi / 2, default=0)
    grip_factor: float = Field(gt=0, default=1)
    sector: str = Field(default="Sector 1")
    lap_number: int = Field(default=1)
    start_coordinate: tuple[float, float] = Field(default=(0, 0))
    end_coordinate: tuple[float, float] = Field(default=(0, 0))
    heading_angle: float = Field(default=0)

    @property
    def radius(self) -> float:
        return 1 / self.curvature

    @property
    def swept_angle(self) -> float:
        return self.length * self.curvature

    @property
    def chord_length(self) -> float:
        if self.curvature == 0:
            return self.length
        else:
            return 2 * self.radius * math.sin(self.swept_angle / 2)

    def y_to_y(self, value: float) -> float:
        return value * math.cos(self.banking)

    def y_to_z(self, value: float) -> float:
        return value * math.sin(self.banking)

    def z_to_x(self, value: float) -> float:
        return value * math.sin(self.inclination)

    def z_to_y(self, value: float) -> float:
        return value * math.sin(self.banking)

    def z_to_z(self, value: float) -> float:
        return value * math.cos(self.banking) * math.cos(self.inclination)


@dataclass
class Mesh(object):
    """
    A mesh of a track.

    Attributes:
        nodes (list[Node]): A list of nodes making up the track.
        configuration (Configuration): The configuration of the track
            (OPEN or CLOSED).
        track_name (str): The name of the track.
    """

    nodes: list[TrackNode]
    configuration: Configuration
    track_name: str
    location: str
    initial_heading: float
    initial_coordinates: tuple[float, float]

    def __post_init__(self) -> None:
        self.calculate_positions()

    def __iter__(self) -> Generator[TrackNode]:
        for node in self.nodes:
            yield node

    @property
    def node_count(self) -> int:
        return len(self.nodes)

    @property
    def track_length(self) -> float:
        return sum(node.length for node in self)

    @property
    def resolution(self) -> float:
        return self.track_length / self.node_count

    def calculate_positions(self) -> None:
        position = 0
        for node in self:
            node.position = position
            position += node.length

    def get_repeating_mesh(self, number_of_laps: int) -> Mesh:
        """
        Generate a new mesh that repeats the track a number of times.

        Args:
            number_of_laps (int): The number of times to repeat the track.

        Returns:
            mesh (Mesh): A new mesh that repeats the track a number of times.
        """

        repeating_nodes: list[TrackNode] = []
        for lap in range(1, number_of_laps + 1):
            new_nodes = copy.deepcopy(self.nodes)
            for node in new_nodes:
                node.lap_number = lap
                repeating_nodes.append(node)

        position = 0
        for node in repeating_nodes:
            node.position = position
            position += node.length

        return Mesh(
            nodes=repeating_nodes,
            configuration=self.configuration,
            track_name=self.track_name,
            location=self.location,
            initial_heading=self.initial_heading,
            initial_coordinates=self.initial_coordinates,
        )

    def plot_traces(self) -> None:
        position = [node.position for node in self]
        curvature = [node.curvature for node in self]
        elevation = [node.elevation for node in self]
        inclination = [node.inclination for node in self]
        banking = [node.banking for node in self]

        data: dict[str, list[float]] = {
            "Curvature": curvature,
            "Elevation": elevation,
            "Inclination": inclination,
            "Banking": banking,
        }

        fig, axs = plt.subplots(len(data), sharex=True)
        fig.suptitle("Track Mesh Parameters")
        axs[-1].set_xlabel("Position")

        i = 0
        for label, ydata in data.items():
            axs[i].plot(position, ydata)
            axs[i].set_title(label)
            axs[i].set_ylabel(label)
            axs[i].grid()
            i += 1
        plt.show()
