"""
This module defines the structure of plot configurations.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from usmlap.core.library import Serialisable
from usmlap.solver.solution_channels import ChannelId


class WaveformConfig(Serialisable):
    """Configuration options for a plot."""

    title: str
    xaxis: XAxisConfig
    axes: list[AxisConfig]


class AxisConfig(BaseModel):
    """Configuration options for an axis of a plot."""

    channels: list[ChannelConfig]
    ylabel: str | None = None
    show_grid: bool = True
    show_legend: bool = True


class ChannelConfig(BaseModel):
    """Configuration options for a single channel."""

    channel_id: ChannelId
    provided_label: str | None = Field(alias="label", default=None)
    colour: str | None = Field(default=None)

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
