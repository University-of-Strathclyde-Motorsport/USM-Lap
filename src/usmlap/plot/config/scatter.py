"""Configuration options for scatter plots."""

from usmlap.core.serialisable import Serialisable
from usmlap.plot.config.axes import AxisConfig, ColourAxisConfig


class ScatterConfig(Serialisable):
    """Configuration options for a scatter plot."""

    title: str
    xaxis: AxisConfig
    yaxis: AxisConfig
    caxis: ColourAxisConfig | None = None
    alpha: float = 1
    show_grid: bool = True
