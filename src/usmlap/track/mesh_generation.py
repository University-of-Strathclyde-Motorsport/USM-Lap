"""
This module contains code for generating a track mesh.
"""

import math
from dataclasses import dataclass
from typing import Any

import numpy as np

from usmlap.utils.array import diff

from .mesh import Mesh, TrackNode
from .track_data import Configuration, TrackData


class Resolution(float):
    """
    Resolution of a track mesh, in metres.
    Must be a positive number.
    """

    def __new__(cls, value: Any) -> None:
        value = float(value)
        if value <= 0:
            raise ValueError("Resolution must be greater than 0")
        return super().__new__(cls, value)


def generate_mesh(
    track_data: TrackData, resolution: float | Resolution
) -> Mesh:
    """
    Generate a track mesh from track data.

    Args:
        track_data (TrackData): The track data object.
        resolution (Resolution): The resolution of the mesh, in metres.

    Returns:
        mesh (Mesh): A mesh of the track.
    """
    resolution = Resolution(resolution)
    return _MeshGenerator(resolution).generate_mesh(track_data)


@dataclass
class _MeshGenerator(object):
    """
    Generates a mesh from a track data object.

    Attributes:
        resolution (Resolution): The target length of a node, in metres.
    """

    resolution: Resolution

    def generate_mesh(self, track_data: TrackData) -> Mesh:
        """
        Generate a mesh from a track data object.

        Args:
            track_data (TrackData): The track data object.

        Returns:
            mesh (Mesh): A mesh of the track.
        """
        track_length = track_data.shape.total_length
        node_count = round(track_length / self.resolution)
        spacing = track_length / (node_count - 1)
        position = np.arange(0, track_length, spacing)

        length = np.diff(np.append(position, track_length))
        curvature = np.array(track_data.shape.interpolate_curvature(position))
        fractional_position = position / track_length

        if track_data.configuration == Configuration.CLOSED:
            curvature = _correct_tangency(
                curvature, length, fractional_position
            )

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


def _correct_tangency(
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
