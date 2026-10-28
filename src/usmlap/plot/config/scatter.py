"""Configuration options for scatter  plots."""

from pydantic import Field

from usmlap.core.library import Serialisable
from usmlap.solver.solution_channels import ChannelId


class AxisConfig(Serialisable):
    """Configuration options for an axis."""

    channel_id: ChannelId
    provided_label: str | None = Field(alias="label", default=None)

    @property
    def label(self) -> str:
        return self.provided_label or self.channel_id


class ScatterConfig(Serialisable):
    """Configuration options for a scatter plot."""

    title: str
    xaxis: AxisConfig
    yaxis: AxisConfig
    caxis: AxisConfig | None = None
    alpha: float = 1
    show_grid: bool = True
