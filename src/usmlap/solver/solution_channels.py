"""
This module implements telemetry channels for a solution.
"""

from __future__ import annotations

import logging
from enum import StrEnum

import numpy as np
import polars

from usmlap.core.types import Array1D
from usmlap.solver import Solution
from usmlap.track import Mesh

logger = logging.getLogger(__name__)


class ChannelId(StrEnum):
    """Enumeration of telemetry channel ids."""

    S_LAP = "sLap"
    LENGTH = "length"
    RADIUS = "radius"
    CURVATURE = "curvature"
    ELEVATION = "elevation"
    INCLINATION = "inclination"
    BANKING = "banking"
    GRIP_FACTOR = "grip_factor"
    SECTOR = "sector"
    N_LAP = "nLap"
    HEADING_ANGLE = "heading_angle"


def extract_channels(solution: Solution) -> dict[ChannelId, Array1D]:
    """Extract channels from a solution to save to file."""
    return {
        ChannelId.S_LAP: np.array(
            [node.track_node.position for node in solution]
        ),
        ChannelId.LENGTH: np.array(
            [node.track_node.length for node in solution]
        ),
        ChannelId.CURVATURE: np.array(
            [node.track_node.radius for node in solution]
        ),
        ChannelId.ELEVATION: np.array(
            [node.track_node.elevation for node in solution]
        ),
    }


def extract_mesh_channels(mesh: Mesh) -> dict[ChannelId, Array1D]:
    """Extract channels from a mesh to save to file."""
    return {
        ChannelId.S_LAP: np.array([node.position for node in mesh]),
        ChannelId.LENGTH: np.array([node.length for node in mesh]),
        ChannelId.CURVATURE: np.array([node.curvature for node in mesh]),
        ChannelId.ELEVATION: np.array([node.elevation for node in mesh]),
        ChannelId.INCLINATION: np.array([node.inclination for node in mesh]),
        ChannelId.BANKING: np.array([node.banking for node in mesh]),
    }


class SolutionDataFrame:
    """This class stores channels in a dataframe."""

    _df: polars.DataFrame

    def __init__(self, df: polars.DataFrame) -> None:
        self._df = df

    @staticmethod
    def from_dataframe(df: polars.DataFrame) -> SolutionDataFrame:
        return SolutionDataFrame(df)

    @staticmethod
    def from_channels(channels: dict[ChannelId, Array1D]) -> SolutionDataFrame:
        return SolutionDataFrame(polars.DataFrame(channels))

    @property
    def channel_count(self) -> int:
        return len(self._df.columns)

    @property
    def row_count(self) -> int:
        return len(self._df)

    def get_channel(
        self, channel_id: ChannelId, *, warn_missing: bool = True
    ) -> Array1D:
        """
        Get a channel from the solution.
        Returns an array of NaN if the channel is missing.
        """
        if channel_id not in self._df.columns:
            if warn_missing:
                logger.warning("Channel '%s' not found", channel_id)
            return np.full(self.row_count, np.nan, dtype=np.float64)
        return self._df[channel_id].to_numpy()
