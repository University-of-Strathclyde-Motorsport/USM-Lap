"""
This module defines nodes and meshes for a track.
"""

from __future__ import annotations

import copy
import math
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
    sector: int = Field(gt=0, default=1)
    start_coordinate: tuple[float, float] = Field(default=(0, 0))
    end_coordinate: tuple[float, float] = Field(default=(0, 0))

    @property
    def radius(self) -> float:
        return 1 / self.curvature

    @property
    def swept_angle(self) -> float:
        return self.length * self.curvature

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


class Mesh(object):
    """
    A mesh of a track.

    Attributes:
        nodes (list[Node]): A list of nodes making up the track.
        configuration (Configuration): The configuration of the track
            (OPEN or CLOSED).
    """

    nodes: list[TrackNode]
    configuration: Configuration

    def __init__(
        self, nodes: list[TrackNode], configuration: Configuration
    ) -> None:
        self.nodes = nodes
        self.configuration = configuration
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

        new_nodes: list[TrackNode] = []
        for _ in range(number_of_laps):
            for node in self:
                new_nodes.append(copy.copy(node))

        position = 0
        for node in new_nodes:
            node.position = position
            position += node.length

        return Mesh(nodes=new_nodes, configuration=self.configuration)

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

    def plot_map(self) -> None:
        coordinates = [node.start_coordinate for node in self]
        coordinates.append(self.nodes[-1].end_coordinate)
        x, y = zip(*coordinates)

        _, ax = plt.subplots()
        ax.set_title("Track Map")

        ax.plot(x, y)
        ax.plot([0, 0], [-10, 10], color="red")
        ax.annotate(
            "",
            xytext=(0, 0),
            xy=(50, 0),
            arrowprops={"arrowstyle": "->", "color": "red"},
        )
        ax.grid()
        plt.show()
