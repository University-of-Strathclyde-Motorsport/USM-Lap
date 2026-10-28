"""Configuration options for waveform plots."""

from __future__ import annotations

from matplotlib.typing import LineStyleType, MarkerType
from pydantic import Field

from usmlap.core.colour import HexColour
from usmlap.core.library import Serialisable
from usmlap.solver.solution_channels import ChannelId


class WaveformConfig(Serialisable):
    """Configuration options for a plot."""

    title: str
    xaxis: XAxisConfig
    axes: list[WaveformAxisConfig]


class XAxisConfig(Serialisable):
    """Configuration options for the x-axis of the plot."""

    channel_id: ChannelId
    provided_label: str | None = Field(alias="label", default=None)

    @property
    def label(self) -> str:
        return self.provided_label or self.channel_id


class WaveformAxisConfig(Serialisable):
    """Configuration options for an axis of a plot."""

    channels: list[ChannelConfig]
    ylabel: str | None = None
    height: float = 1
    show_grid: bool = True
    show_legend: bool = True


class ChannelConfig(Serialisable):
    """Configuration options for a single channel."""

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
