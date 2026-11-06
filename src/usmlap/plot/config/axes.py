"""Configuration options for axes."""

from pydantic import Field

from usmlap.core.serialisable import Serialisable
from usmlap.solver.solution_channels import ChannelId


class AxisConfig(Serialisable):
    """Configuration options for an axis."""

    channel_id: ChannelId
    provided_label: str | None = Field(alias="label", default=None)

    @property
    def label(self) -> str:
        return self.provided_label or self.channel_id


class ColourAxisConfig(AxisConfig):
    """Configuration options for an axis, including colour channels."""

    cmap: str = Field(default="viridis")
    cmin: float | None = None
    cmax: float | None = None

    def get_new_clim(self, old: tuple[float, float]) -> tuple[float, float]:
        old_min, old_max = old
        new_min = self.cmin or old_min
        new_max = self.cmax or old_max
        return (new_min, new_max)
