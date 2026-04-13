"""
This module contains code for generating a track mesh.
"""

import math
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

type Array = np.ndarray[tuple[int], np.dtype[np.float64]]

MAX_TANGENCY_CORRECTION_ITERATIONS = 100
ACCEPTABLE_TANGENCY_ERROR = 1e-4
MAX_DISPLACEMENT_CORRECTION_ITERATIONS = 200
ACCEPTABLE_DISPLACEMENT_ERROR = 1e-3


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
    track_data: TrackData,
    resolution: float | Resolution,
    *,
    smooth: bool = True,
    initial_heading: float = 0,
    initial_coordinates: tuple[float, float] = (0, 0),
    correct_tangency: bool = True,
    correct_displacement: bool = True,
) -> Mesh:
    """
    Generate a track mesh from track data.

    Args:
        track_data (TrackData): The track data object.
        resolution (Resolution): The resolut     ion of the mesh, in metres.
        smooth (bool): Whether to smooth the curvature data (default = `True`).
        correct_tangency (bool): Whether to apply tangency correction
            to the track (default = `True`).
        correct_displacement (bool): Whether to apply displacement correction
            to the track (default = `True`).


    Returns:
        mesh (Mesh): A mesh of the track.
    """
    resolution = Resolution(resolution)

    track_length = track_data.total_length
    node_count = round(track_length / resolution)
    spacing = track_length / (node_count - 1)
    position = np.arange(0, track_length, spacing)

    length = np.diff(np.append(position, track_length))
    curvature = _interpolate_curvature(
        track_data.shape, position, smooth=smooth
    )

    elevation = _interpolate_elevation(track_data.elevation, position)
    banking = _interpolate_banking(track_data.banking, position)
    grip_factor = _interpolate_grip_factor(track_data.grip_factor, position)
    sector = _interpolate_sector(track_data.sectors, position)
    inclination = _calculate_inclination(position, elevation)

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

    if correct_tangency and track_data.configuration == Configuration.CLOSED:
        nodes = _correct_tangency(nodes)

    if (
        correct_displacement
        and track_data.configuration == Configuration.CLOSED
    ):
        nodes = _correct_displacement(nodes)

    nodes = _set_heading_angle(nodes, initial_heading)
    nodes = _set_coordinates(nodes, initial_coordinates)

    return Mesh(
        nodes=nodes,
        configuration=track_data.configuration,
        track_name=track_data.print_name,
        location=track_data.location,
        initial_heading=initial_heading,
        initial_coordinates=initial_coordinates,
    )


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
    length = np.array([node.length for node in data])
    position = np.cumsum(length) - (0.5 * length)
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


def _calculate_inclination(position: NDArray, elevation: NDArray) -> NDArray:
    """
    Calculate the inclination of the track.

    Args:
        position (NDArray): A list of positions.
        elevation (NDArray): The elevation at each position.

    Returns:
        inclination (NDArray): The inclination at each position.
    """
    diff_position = np.diff(position)
    diff_elevation = np.diff(elevation)

    inclination_position = position[:-1] + diff_position / 2
    inclination_value = np.atan(diff_elevation / diff_position)

    inclination = np.interp(position, inclination_position, inclination_value)
    return inclination


def _calculate_heading_angle(
    length: NDArray, curvature: NDArray, initial_heading: float = 0
) -> NDArray:
    """
    Calculate the heading angle for each node of a track.

    Args:
        length (NDArray): The length of each node.
        curvature (NDArray): The curvature of each node.
        initial_heading (float): The initial heading angle (default = 0).

    Returns:
        heading (NDArray): The heading angle for each node.
    """

    swept_angle = curvature * length
    heading = initial_heading + np.cumsum(swept_angle) - swept_angle[0]
    return heading


def _set_heading_angle(
    nodes: list[TrackNode], initial_heading: float = 0
) -> list[TrackNode]:
    """
    Set the heading angle of each node in a list.

    Args:
        nodes (list[TrackNode]): The nodes to update.
        initial_heading (float): The initial heading angle (default = 0).

    Returns:
        nodes (list[TrackNode]): The updated nodes.
    """

    curvature = np.array([node.curvature for node in nodes])
    length = np.array([node.length for node in nodes])
    heading = _calculate_heading_angle(length, curvature, initial_heading)

    for i, node in enumerate(nodes):
        node.heading_angle = heading[i]

    return nodes


def _calculate_coordinates(
    length: NDArray,
    curvature: NDArray,
    initial_coordinates: tuple[float, float] = (0, 0),
) -> tuple[NDArray, NDArray]:
    """
    Calculate the coordinates for each node of a track.

    Note that the lengths of the returned arrays are one greater
    than the length of the input arrays.
    The first to penultimate elements are the start coordinates of each node.
    The second to final elements are the end coordinates of each node.

    Args:
        length (NDArray): The length of each node.
        curvature (NDArray): The curvature of each node.
        initial_coordinates (tuple[float, float]):
            The initial x and y coordinates (default = (0, 0)).

    Returns:
        coordinates (tuple[NDArray, NDArray]): Lists of x and y coordinates.
    """

    x_0, y_0 = initial_coordinates

    swept_angle = curvature * length
    heading = _calculate_heading_angle(length, curvature, 0)

    chord_length = length
    idx = curvature != 0
    chord_length[idx] = (2 / curvature[idx]) * np.sin(swept_angle[idx] / 2)

    dx = np.cos(heading) * chord_length
    dy = np.sin(heading) * chord_length
    x = np.concatenate(([x_0], x_0 + np.cumsum(dx)))
    y = np.concatenate(([y_0], y_0 + np.cumsum(dy)))

    return x, y


def _set_coordinates(
    nodes: list[TrackNode], initial_coordinates: tuple[float, float] = (0, 0)
) -> list[TrackNode]:
    """
    Set the heading angle and coordinates of each node in a list.

    Args:
        nodes (list[TrackNode]): The nodes to update.
        initial_coordinates (tuple[float, float]): The start coordinate
            of the first node (default = (0, 0)).

    Returns:
        nodes (list[TrackNode]): The updated nodes.
    """

    length = np.array([node.length for node in nodes])
    curvature = np.array([node.curvature for node in nodes])
    x, y = _calculate_coordinates(length, curvature, initial_coordinates)

    for i, node in enumerate(nodes):
        node.start_coordinate = (x[i], y[i])
        node.end_coordinate = (x[i + 1], y[i + 1])

    return nodes


def _correct_tangency(
    nodes: list[TrackNode], iterations: int = MAX_TANGENCY_CORRECTION_ITERATIONS
) -> list[TrackNode]:
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

    curvature = np.array([node.curvature for node in nodes])
    length = np.array([node.length for node in nodes])

    for i in range(iterations):
        heading_angle = _calculate_heading_angle(length, curvature, 0)

        heading_difference = heading_angle[-1] - heading_angle[0]
        tangency_error = math.remainder(heading_difference, 2 * math.pi)

        if abs(tangency_error) < ACCEPTABLE_TANGENCY_ERROR:
            break
        elif abs(tangency_error) < math.pi:  # 'Uncurl' the track
            tangency_correction = -tangency_error
        else:  # 'Curl' the track
            tangency_correction = (
                2 * math.pi * np.sign(tangency_error) - tangency_error
            )

        abs_curvature = abs(curvature)
        correction_factor = abs_curvature / sum(abs_curvature)
        curvature += tangency_correction * correction_factor

    for i, node in enumerate(nodes):
        node.curvature = curvature[i]

    nodes = _set_heading_angle(nodes)
    return nodes


def _correct_displacement(
    nodes: list[TrackNode],
    iterations: int = MAX_DISPLACEMENT_CORRECTION_ITERATIONS,
) -> list[TrackNode]:
    """
    Adjust the length and curvature of each node
    to correct a displacement error.

    Args:
        nodes (list[TrackNode]): The nodes of the track.
        iterations (int): The number of iterations to run.

    Returns:
        corrected_nodes (list[TrackNode]): The corrected nodes.
    """
    original_length = sum([node.length for node in nodes])
    length = np.array([node.length for node in nodes])
    curvature = np.array([node.curvature for node in nodes])

    for i in range(iterations):
        x, y = _calculate_coordinates(length, curvature, (0, 0))
        coordinates = np.stack((x, y))
        error = coordinates[:, -1] - coordinates[:, 0]
        error_magnitude = np.linalg.norm(error)
        unit_error = error / error_magnitude

        if error_magnitude < ACCEPTABLE_DISPLACEMENT_ERROR:
            break

        displacements = np.diff(coordinates, axis=1)
        agreement_factor = -np.dot(displacements.T, unit_error)
        abs_agreement = sum(abs(agreement_factor))

        sigma = 1 + (error_magnitude * agreement_factor / abs_agreement)
        length *= sigma
        curvature /= sigma

        stretch_factor = original_length / sum(length)
        length *= stretch_factor
        curvature /= stretch_factor

    for i in range(len(nodes)):
        nodes[i].length = length[i]
        nodes[i].curvature = curvature[i]

    return nodes
