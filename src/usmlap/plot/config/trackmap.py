"""Configuration options for trackmap plots."""

from usmlap.core.colour import HexColour
from usmlap.core.serialisable import Serialisable
from usmlap.plot.config.axes import ColourAxisConfig


class TrackmapConfig(Serialisable):
    """Configuration options for a trackmap plot."""

    title: str | None = None
    caxis: ColourAxisConfig | None = None
    show_grid: bool = True
    show_start_line: bool = True
    start_line_colour: HexColour = HexColour("#000000")
    line_width: float = 10
