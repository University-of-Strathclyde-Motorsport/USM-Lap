"""
This module defines the structure of plot configurations.
"""

from __future__ import annotations

from matplotlib.typing import LineStyleType, MarkerType
from pydantic import BaseModel, ConfigDict, Field

from usmlap.core.colour import HexColour
from usmlap.core.library import Serialisable
from usmlap.solver.solution_channels import ChannelId


class WaveformConfig(Serialisable):
    """Configuration options for a plot."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    title: str
    xaxis: XAxisConfig
    axes: list[AxisConfig]


class AxisConfig(Serialisable):
    """Configuration options for an axis of a plot."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    channels: list[ChannelConfig]
    ylabel: str | None = None
    height: float = 1
    show_grid: bool = True
    show_legend: bool = True


class ChannelConfig(Serialisable):
    """Configuration options for a single channel."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    channel_id: ChannelId
    provided_label: str | None = Field(alias="label", default=None)
    colour: HexColour = HexColour("#003366")
    linestyle: LineStyleType = "solid"
    marker: MarkerType = "none"
    marker_colour: HexColour = HexColour("#003366")
    marker_edge_width: float = 0
    gate_channel: ChannelId | None = None

    @property
    def label(self) -> str:
        return self.provided_label or self.channel_id


class XAxisConfig(BaseModel):
    """Configuration options for the x-axis of the plot."""

    channel_id: ChannelId
    provided_label: str | None = Field(alias="label", default=None)

    @property
    def label(self) -> str:
        return self.provided_label or self.channel_id
