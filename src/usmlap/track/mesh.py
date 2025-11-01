"""
This module contains code for generating a track mesh.
"""

from __future__ import annotations
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass
from typing import Annotated
from annotated_types import Unit
from math import pi, atan, ceil
import copy
import numpy as np
import matplotlib.pyplot as plt

from .track_data import Configuration, TrackData
from utils.array import diff


ENDURANCE_TRACK_LENGTH = 22000


class Node(BaseModel):
    """
    A node of a track.

    Attributes:
        Position (float): The position of the node from the start of the track.
        Length (float): The length of the track section.
        Curvature (float): The curvature of the track section.
        Elevation (float): The elevation of the track section.
        Inclination (float): The inclination angle of the track section.
        Banking (float): The banking angle of the track section.
        GripFactor (float): The grip factor of the track section.
        Sector (int): The sector of the track section.
    """

    position: float = Field(ge=0)
    length: float = Field(gt=0)
    curvature: float
    elevation: float
    inclination: float = Field(gt=-pi / 2, lt=pi / 2, default=0)
    banking: float = Field(ge=-pi / 2, le=pi / 2, default=0)
    grip_factor: float = Field(gt=0, default=1)
    sector: int = Field(gt=0, default=1)


class Mesh(BaseModel):
    """
    A mesh of a track.

    Attributes:
        nodes (list[Node]): A list of nodes making up the track.
        configuration (Configuration): The configuration of the track
            (OPEN or CLOSED).
    """

    nodes: list[Node]
    configuration: Configuration

    @property
    def node_count(self) -> float:
        return len(self.nodes)

    @property
    def track_length(self) -> float:
        return sum(node.length for node in self.nodes)

    @property
    def resolution(self) -> float:
        return self.track_length / self.node_count

    def generate_endurance_mesh(self) -> Mesh:
        number_of_laps = ceil(ENDURANCE_TRACK_LENGTH / self.track_length)

        endurance_nodes: list[Node] = []
        for _ in range(number_of_laps):
            for node in self.nodes:
                endurance_nodes.append(copy.copy(node))

        position = 0
        for node in endurance_nodes:
            node.position = position
            position += node.length

        return Mesh(nodes=endurance_nodes, configuration=self.configuration)

    def plot_traces(self) -> None:
        position = [node.position for node in self.nodes]
        curvature = [node.curvature for node in self.nodes]
        elevation = [node.elevation for node in self.nodes]
        inclination = [node.inclination for node in self.nodes]
        banking = [node.banking for node in self.nodes]

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


@dataclass
class MeshGenerator(object):
    """
    Generates a mesh from a track data object.

    Attributes:
        resolution (float): The target length of a node in meters.
    """

    resolution: Annotated[float, Field(gt=0, default=1), Unit("m")]

    def generate_mesh(self, track_data: TrackData) -> Mesh:
        """
        Generate a mesh from a track data object.

        Args:
            track_data (TrackData): The track data object.

        Returns:
            mesh (Mesh): A mesh of the track.
        """
        self.track_data = track_data
        self.track_length = track_data.shape.total_length
        self.node_count = round(self.track_length / self.resolution)
        self.spacing = self.track_length / (self.node_count - 1)
        self.position = np.arange(0, self.track_length, self.spacing).tolist()

        length = diff(self.position + [self.track_length])
        curvature = track_data.shape.interpolate_curvature(self.position)
        # TODO: Implement code for closing the track
        # fractional_position = [p / self.track_length for p in position]

        elevation = track_data.elevation.interpolate(self.position)
        banking = track_data.banking.interpolate(self.position)
        grip_factor = track_data.grip_factor.interpolate(self.position)
        sector = track_data.sector.interpolate(self.position)
        inclination = self._calculate_inclination(self.position, elevation)

        nodes = [
            Node(
                position=self.position[i],
                length=length[i],
                curvature=curvature[i],
                elevation=elevation[i],
                inclination=inclination[i],
                banking=banking[i],
                grip_factor=grip_factor[i],
                sector=sector[i],
            )
            for i in range(len(self.position))
        ]

        return Mesh(nodes=nodes, configuration=track_data.configuration)

    @staticmethod
    def _calculate_inclination(
        position: list[float], elevation: list[float]
    ) -> list[float]:
        diff_position = diff(position)
        diff_elevation = diff(elevation)
        inclination_position = [
            position[i] + diff_position[i] / 2
            for i in range(len(diff_position))
        ]
        inclination_value = [
            atan(diff_elevation[i] / diff_position[i])
            for i in range(len(diff_position))
        ]
        return np.interp(
            position, inclination_position, inclination_value
        ).tolist()
