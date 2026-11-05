"""This module defines settings for track mesh generation."""

from __future__ import annotations

from pathlib import Path

from usmlap.core.serialisable import Serialisable


class TrackSettings(Serialisable):
    """Settings for track mesh generation.

    Properties:
        track_file (Path): A track data file.
        resolution (float): The resolution of the mesh, in metres.
        smooth (bool): Whether to smooth the curvature data (default =
            ``True``).
        correct_tangency (bool): Whether to apply tangency correction to the
            track (default = ``True``).
        correct_displacement (bool): Whether to apply displacement correction to
            the track (default = ``True``).
    """

    track_file: Path
    resolution: float
    smooth: bool = True
    initial_heading: float = 0
    initial_coordinates: tuple[float, float] = (0, 0)
    correct_tangency: bool = True
    correct_displacement: bool = True
    tangency_correction_maximum_iterations: int = 100
    tangency_correction_acceptable_error: float = 1e-4
    displacement_correction_maximum_iterations: int = 200
    displacement_correction_acceptable_error: float = 1e-3
