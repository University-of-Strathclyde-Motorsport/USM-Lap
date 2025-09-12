"""
This module contains code for generating a track mesh.
"""

from pydantic import BaseModel, Field
from math import pi, atan
from itertools import accumulate
import numpy as np

from .track_data import Configuration, TrackData
from utils.array import diff, cumsum


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


class MeshGenerator(object):
    """
    Generates a mesh from a track data object.
    """

    def generate_mesh(self, track_data: TrackData) -> Mesh:
        """
        Generate a mesh from a track data object.

        Args:
            track_data (TrackData): The track data object.

        Returns:
            mesh (Mesh): A mesh of the track.
        """
        self.track_data = track_data
        self.track_length = track_data.total_length

        length = [shape.length for shape in track_data.shape]
        position = list(accumulate(length))
        position.insert(0, 0)
        position.pop()
        # fractional_position = [p / self.track_length for p in position]

        curvature = self._interpolate_curvature(position)
        # TODO: Implement code for closing the track

        elevation = track_data.elevation.interpolate(position)
        banking = track_data.banking.interpolate(position)
        grip_factor = track_data.grip_factor.interpolate(position)
        sector = track_data.sector.interpolate(position)

        inclination = self._calculate_inclination(position, elevation)

        nodes = [
            Node(
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

        return Mesh(nodes=nodes, configuration=track_data.configuration)

    def _interpolate_curvature(self, position: list[float]) -> list[float]:
        curvature_position = cumsum([s.length for s in self.track_data.shape])
        curvature_value = [s.curvature for s in self.track_data.shape]
        if self.track_data.configuration == Configuration.CLOSED:
            curvature_position.append(curvature_position[0] + self.track_length)
            curvature_value.append(curvature_value[0])
        return np.interp(position, curvature_position, curvature_value).tolist()

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
