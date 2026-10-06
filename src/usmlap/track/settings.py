"""
This module defines settings for track mesh generation.
"""

from __future__ import annotations

from pathlib import Path

from usmlap.core.library import SupportsLoading


class TrackSettings(SupportsLoading):
    """Settings for track mesh generation."""

    track_file: Path
    resolution: float
    smooth: bool = True
    initial_heading: float = 0
    initial_coordinates: tuple[float, float] = (0, 0)
    correct_tangency: bool = True
    correct_displacement: bool = True
    tangency_correction_maximum_iterations: int = 100
    tangency_correction_acceptable_error = 1e-4
    displacement_correction_maximum_iterations: int = 200
    displacement_correction_acceptable_error = 1e-3
