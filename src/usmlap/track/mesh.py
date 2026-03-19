"""
This module contains code for generating a track mesh.
"""

from __future__ import annotations

import copy
import math
from typing import Annotated, Generator

import matplotlib.pyplot as plt
import numpy as np
from annotated_types import Unit
from pydantic import BaseModel, Field
from pydantic.dataclasses import dataclass

from usmlap.utils.array import diff

from .track_data import Configuration, TrackData


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
        track_data = track_data
        track_length = track_data.shape.total_length
        node_count = round(track_length / self.resolution)
        spacing = track_length / (node_count - 1)
        position = np.arange(0, track_length, spacing)

        length = np.diff(np.append(position, track_length))
        curvature = np.array(track_data.shape.interpolate_curvature(position))
        fractional_position = position / track_length

        if track_data.configuration == Configuration.CLOSED:
            curvature = correct_tangency(curvature, length, fractional_position)

        # TODO: Implement code for closing the track

        elevation = track_data.elevation.interpolate(position)
        banking = track_data.banking.interpolate(position)
        grip_factor = track_data.grip_factor.interpolate(position)
        sector = track_data.sector.interpolate(position)
        inclination = self._calculate_inclination(position, elevation)

        nodes = [
            TrackNode(
                position=position[i],
                length=length[i],
                curvature=curvature[i],
                elevation=elevation[i],
                inclination=inclination[i],
                banking=banking[i],
                grip_factor=grip_factor[i],
                sector=sector[i],
            )
            for i in range(len(position))
        ]

        close_track = track_data.configuration == Configuration.CLOSED
        nodes = self._set_coordinates(nodes, close_track)

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
            math.atan(diff_elevation[i] / diff_position[i])
            for i in range(len(diff_position))
        ]
        return np.interp(
            position, inclination_position, inclination_value
        ).tolist()

    @staticmethod
    def _set_coordinates(
        nodes: list[TrackNode], close_track: bool
    ) -> list[TrackNode]:
        cursor = (0, 0)
        heading = 0

        for node in nodes:
            node.start_coordinate = cursor
            heading += node.swept_angle
            cursor = (
                cursor[0] + math.cos(heading) * node.length,
                cursor[1] + math.sin(heading) * node.length,
            )
            node.end_coordinate = cursor

        if not close_track:
            return nodes

        error_x = nodes[-1].end_coordinate[0]
        error_y = nodes[-1].end_coordinate[1]
        unit_error_x = error_x / len(nodes)
        unit_error_y = error_y / len(nodes)
        for i, node in enumerate(nodes):
            start_x = node.start_coordinate[0] - (i * unit_error_x)
            start_y = node.start_coordinate[1] - (i * unit_error_y)
            node.start_coordinate = (start_x, start_y)

            end_x = node.end_coordinate[0] - ((i + 1) * unit_error_x)
            end_y = node.end_coordinate[1] - ((i + 1) * unit_error_y)
            node.end_coordinate = (end_x, end_y)

        return nodes


type Array = np.ndarray[tuple[int], np.dtype[np.float64]]


def correct_tangency(
    curvature: Array, length: Array, fractional_position: Array
) -> Array:
    """
    Adjust track curvature to correct the tangency of closed tracks.

    The tangency error is calculated by summing the sweep angle of each node.

    Args:
        curvature (list[float]): The curvature of each node.
        length (list[float]): The length of each node.
        fractional_position (list[float]): The fractional position of each node.

    Returns:
        corrected_curvature (list[float]): Corrected curvature of each node.
    """

    sweep_angle = curvature * length
    heading_angle = np.cumsum(sweep_angle)
    tangency_error = math.remainder(heading_angle[-1], 2 * math.pi)

    if abs(tangency_error) < math.pi:  # 'Uncurl' the track
        tangency_correction = -tangency_error
    else:  # 'Curl' the track
        tangency_correction = (
            2 * math.pi * np.sign(tangency_error) - tangency_error
        )

    heading_angle = heading_angle + (fractional_position * tangency_correction)
    sweep_angle = np.array([heading_angle[0], *np.diff(heading_angle)])
    curvature = sweep_angle / length
    return curvature
