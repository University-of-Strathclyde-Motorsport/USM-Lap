"""
This module contains code for generating a track mesh."""

import math

import numpy as np

from usmlap.core.types import Array1D
from usmlap.track.mesh import Mesh, TrackNode
from usmlap.track.settings import TrackSettings
from usmlap.track.track_data import (
    BankingData,
    Configuration,
    ElevationData,
    GripFactorData,
    SectorData,
    ShapeData,
    TrackData,
)
from usmlap.utils.array import interp_previous


def generate_mesh(settings: TrackSettings) -> Mesh:
    """
    Generate a track mesh from track data.

    Args:
        track_data (TrackData): The track data object.
        resolution (float): The resolution of the mesh, in metres.
        smooth (bool): Whether to smooth the curvature data (default = `True`).
        correct_tangency (bool): Whether to apply tangency correction
            to the track (default = `True`).
        correct_displacement (bool): Whether to apply displacement correction
            to the track (default = `True`).


    Returns:
        mesh (Mesh): A mesh of the track.

    """
    track_data = TrackData.from_json(settings.track_file)
    track_length = track_data.total_length
    node_count = round(track_length / settings.resolution)
    spacing = track_length / (node_count - 1)
    position = np.arange(0, track_length, spacing).astype(np.float64)

    length = np.diff(np.append(position, track_length))
    curvature = _interpolate_curvature(
        track_data.shape, position, smooth=settings.smooth
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

    if track_data.configuration == Configuration.CLOSED:
        if settings.correct_tangency:
            nodes = _correct_tangency(nodes, settings)

        if settings.correct_displacement:
            nodes = _correct_displacement(nodes, settings)

    nodes = _set_heading_angle(nodes, settings.initial_heading)
    nodes = _set_coordinates(nodes, settings.initial_coordinates)

    return Mesh(
        nodes=nodes,
        configuration=track_data.configuration,
        track_name=track_data.print_name,
        location=track_data.location,
        initial_heading=settings.initial_heading,
        initial_coordinates=settings.initial_coordinates,
    )


def _interpolate_curvature(
    data: list[ShapeData],
    sample_position: Array1D,
    smooth: bool = True,
) -> Array1D:
    """
    Interpolate the curvature of the track at a series of positions.

    Args:
        data (list[ShapeData]): Shape data for the track.
        sample_position (Array1D): The positions to interpolate at.
        smooth (bool | None): Whether to smooth the curvature
            (default = `True`).
            If `True`, uses `np.interp` to interpolate the curvature.
            If `False`, uses `interp_previous` to interpolate the curvature
    Returns:
        curvature (Array1D): The interpolated curvature.

    """
    curvature = np.array([node.curvature for node in data])
    length = np.array([node.length for node in data])
    position = np.cumsum(length) - (0.5 * length)
    if smooth:
        interpolated = np.interp(sample_position, position, curvature)
    else:
        interpolated = np.array(
            interp_previous(
                sample_position.tolist(),
                position.tolist(),
                curvature.tolist(),
            ),
        )
    return interpolated


def _interpolate_elevation(
    data: list[ElevationData],
    sample_position: Array1D,
) -> Array1D:
    """
    Interpolate the elevation of the track at a series of positions.

    Args:
        data (list[ElevationData]): Elevation data for the track.
        sample_position (Array1D): The positions to interpolate at.

    Returns:
        elevation (Array1D): The interpolated elevation.

    """
    if not data:
        return np.full(len(sample_position), ElevationData.default())
    elevation = np.array([node.elevation for node in data])
    position = np.array([node.position for node in data])
    return np.interp(sample_position, position, elevation)


def _interpolate_banking(
    data: list[BankingData],
    sample_position: Array1D,
) -> Array1D:
    """
    Interpolate the banking of the track at a series of positions.

    Args:
        data (list[BankingData]): Banking data for the track.
        sample_position (Array1D): The positions to interpolate at.

    Returns:
        banking (Array1D): The interpolated banking.

    """
    if not data:
        return np.full(len(sample_position), BankingData.default())
    banking = np.array([node.angle for node in data])
    position = np.array([node.position for node in data])
    return np.interp(sample_position, position, banking)


def _interpolate_grip_factor(
    data: list[GripFactorData],
    sample_position: Array1D,
) -> Array1D:
    """
    Interpolate the grip factor of the track at a series of positions.

    Args:
        data (list[GripFactorData]): Grip factor data for the track.
        sample_position (Array1D): The positions to interpolate at.

    Returns:
        grip_factor (Array1D): The interpolated grip factor.

    """
    if not data:
        return np.full(len(sample_position), GripFactorData.default())
    grip_factor = np.array([node.grip_factor for node in data])
    position = np.array([node.position for node in data])
    return np.interp(sample_position, position, grip_factor)


def _interpolate_sector(
    data: list[SectorData],
    sample_position: Array1D,
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
    return interp_previous(list(sample_position), start_position, label)


def _calculate_inclination(position: Array1D, elevation: Array1D) -> Array1D:
    """
    Calculate the inclination of the track.

    Args:
        position (Array1D): A list of positions.
        elevation (Array1D): The elevation at each position.

    Returns:
        inclination (Array1D): The inclination at each position.

    """
    diff_position = np.diff(position)
    diff_elevation = np.diff(elevation)

    inclination_position = position[:-1] + diff_position / 2
    inclination_value = np.atan(diff_elevation / diff_position)

    inclination = np.interp(position, inclination_position, inclination_value)
    return inclination


def _calculate_heading_angle(
    length: Array1D,
    curvature: Array1D,
    initial_heading: float = 0,
) -> Array1D:
    """
    Calculate the heading angle for each node of a track.

    Args:
        length (Array1D): The length of each node.
        curvature (Array1D): The curvature of each node.
        initial_heading (float): The initial heading angle (default = 0).

    Returns:
        heading (Array1D): The heading angle for each node.

    """
    swept_angle = curvature * length
    heading = initial_heading + np.cumsum(swept_angle) - swept_angle[0]
    return heading


def _set_heading_angle(
    nodes: list[TrackNode],
    initial_heading: float = 0,
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
    length: Array1D,
    curvature: Array1D,
    initial_coordinates: tuple[float, float] = (0, 0),
) -> tuple[Array1D, Array1D]:
    """
    Calculate the coordinates for each node of a track.

    Note that the lengths of the returned arrays are one greater
    than the length of the input arrays.
    The first to penultimate elements are the start coordinates of each node.
    The second to final elements are the end coordinates of each node.

    Args:
        length (Array1D): The length of each node.
        curvature (Array1D): The curvature of each node.
        initial_coordinates (tuple[float, float]):
            The initial x and y coordinates (default = (0, 0)).

    Returns:
        coordinates (tuple[Array1D, Array1D]): Lists of x and y coordinates.

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
    nodes: list[TrackNode],
    initial_coordinates: tuple[float, float] = (0, 0),
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
    nodes: list[TrackNode], settings: TrackSettings
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

    for _ in range(settings.tangency_correction_maximum_iterations):
        heading_angle = _calculate_heading_angle(length, curvature, 0)

        heading_difference = heading_angle[-1] - heading_angle[0]
        tangency_error = math.remainder(heading_difference, 2 * math.pi)

        if abs(tangency_error) < settings.tangency_correction_acceptable_error:
            break
        if abs(tangency_error) < math.pi:  # 'Uncurl' the track
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
    nodes: list[TrackNode], settings: TrackSettings
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

    for _ in range(settings.displacement_correction_maximum_iterations):
        x, y = _calculate_coordinates(length, curvature, (0, 0))
        coordinates = np.stack((x, y))
        error = coordinates[:, -1] - coordinates[:, 0]
        error_magnitude = np.linalg.norm(error)
        unit_error = error / error_magnitude

        if error_magnitude < settings.displacement_correction_acceptable_error:
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
