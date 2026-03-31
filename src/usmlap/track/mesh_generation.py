"""
This module contains code for generating a track mesh.
"""

import math
from dataclasses import dataclass
from typing import Any

import numpy as np

from usmlap.utils.array import interp_previous

from .mesh import Mesh, TrackNode
from .track_data import (
    BankingData,
    Configuration,
    ElevationData,
    GripFactorData,
    SectorData,
    ShapeData,
    TrackData,
)

type NDArray = np.ndarray[tuple[Any, ...], np.dtype[np.float64]]


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


def _interpolate_curvature(
    data: list[ShapeData], sample_position: NDArray, smooth: bool = True
) -> NDArray:
    """
    Interpolate the curvature of the track at a series of positions.

    Args:
        data (list[ShapeData]): Shape data for the track.
        sample_position (NDArray): The positions to interpolate at.
        smooth (Optional[bool]): Whether to smooth the curvature
            (default = `True`).
            If `True`, uses `np.interp` to interpolate the curvature.
            If `False`, uses `interp_previous` to interpolate the curvature
    Returns:
        curvature (NDArray): The interpolated curvature.
    """
    curvature = np.array([node.curvature for node in data])
    position = np.cumsum([node.length for node in data])
    if smooth:
        interpolated = np.interp(sample_position, position, curvature)
    else:
        interpolated = np.array(
            interp_previous(
                sample_position.tolist(), position.tolist(), curvature.tolist()
            )
        )
    return interpolated


def _interpolate_elevation(
    data: list[ElevationData], sample_position: NDArray
) -> NDArray:
    """
    Interpolate the elevation of the track at a series of positions.

    Args:
        data (list[ElevationData]): Elevation data for the track.
        sample_position (NDArray): The positions to interpolate at.

    Returns:
        elevation (NDArray): The interpolated elevation.
    """
    if not data:
        return np.full(len(sample_position), ElevationData.default())
    elevation = np.array([node.elevation for node in data])
    position = np.array([node.position for node in data])
    return np.interp(sample_position, position, elevation)


def _interpolate_banking(
    data: list[BankingData], sample_position: NDArray
) -> NDArray:
    """
    Interpolate the banking of the track at a series of positions.

    Args:
        data (list[BankingData]): Banking data for the track.
        sample_position (NDArray): The positions to interpolate at.

    Returns:
        banking (NDArray): The interpolated banking.
    """
    if not data:
        return np.full(len(sample_position), BankingData.default())
    banking = np.array([node.angle for node in data])
    position = np.array([node.position for node in data])
    return np.interp(sample_position, position, banking)


def _interpolate_grip_factor(
    data: list[GripFactorData], sample_position: NDArray
) -> NDArray:
    """
    Interpolate the grip factor of the track at a series of positions.

    Args:
        data (list[GripFactorData]): Grip factor data for the track.
        sample_position (NDArray): The positions to interpolate at.

    Returns:
        grip_factor (NDArray): The interpolated grip factor.
    """
    if not data:
        return np.full(len(sample_position), GripFactorData.default())
    grip_factor = np.array([node.grip_factor for node in data])
    position = np.array([node.position for node in data])
    return np.interp(sample_position, position, grip_factor)


def _interpolate_sector(
    data: list[SectorData], sample_position: list[float]
) -> list[str]:
    """
    Interpolate the sector of the track at a series of positions.

    Args:
        data (list[SectorData]): Sector data for the track.
        sample_position (list[float]): The positions to interpolate at.

    Returns:
        sector (list[str]): The interpolated sector.
    """
    if not data:
        return [SectorData.default()] * len(sample_position)
    label = [node.label for node in data]
    start_position = [node.start_position for node in data]
    return interp_previous(sample_position, start_position, label)


def generate_mesh(
    track_data: TrackData, resolution: float | Resolution, smooth: bool = True
) -> Mesh:
    """
    Generate a track mesh from track data.

    Args:
        track_data (TrackData): The track data object.
        resolution (Resolution): The resolution of the mesh, in metres.
        smooth (bool): Whether to smooth the curvature data (default = `True`).

    Returns:
        mesh (Mesh): A mesh of the track.
    """
    mesh_generator = _MeshGenerator(Resolution(resolution), smooth)
    return mesh_generator.generate_mesh(track_data)


@dataclass
class _MeshGenerator(object):
    """
    Generates a mesh from a track data object.

    Attributes:
        resolution (Resolution): The target length of a node, in metres.
        smooth (bool): Whether to smooth the curvature data (default = `True`).
    """

    resolution: Resolution
    smooth: bool = True

    def generate_mesh(self, track_data: TrackData) -> Mesh:
        """
        Generate a mesh from a track data object.

        Args:
            track_data (TrackData): The track data object.

        Returns:
            mesh (Mesh): A mesh of the track.
        """
        track_length = track_data.total_length
        node_count = round(track_length / self.resolution)
        spacing = track_length / (node_count - 1)
        position = np.arange(0, track_length, spacing)

        length = np.diff(np.append(position, track_length))
        curvature = _interpolate_curvature(
            track_data.shape, position, smooth=self.smooth
        )
        fractional_position = position / track_length

        if track_data.configuration == Configuration.CLOSED:
            curvature = _correct_tangency(
                curvature, length, fractional_position
            )

        # TODO: Implement code for closing the track

        elevation = _interpolate_elevation(track_data.elevation, position)
        banking = _interpolate_banking(track_data.banking, position)
        grip_factor = _interpolate_grip_factor(track_data.grip_factor, position)
        sector = _interpolate_sector(track_data.sectors, position)
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
        position: np.ndarray, elevation: np.ndarray
    ) -> list[float]:
        diff_position = np.diff(position)
        diff_elevation = np.diff(elevation)
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
