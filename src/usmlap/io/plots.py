"""
This module saves matplotlib figures to disk.
"""

import logging
from pathlib import Path

from matplotlib.figure import Figure

logger = logging.getLogger(__name__)


def save_figure(
    figure: Figure,
    filepath: Path,
    *,
    size: tuple[int, int] = (15, 9),
    dpi: float = 100,
    format: str = "png",
) -> None:
    """Save a matplotlib figure."""
    filepath = filepath.with_suffix(f".{format}")
    filepath.parent.mkdir(parents=True, exist_ok=True)
    width, height = size
    figure.set_figheight(height)
    figure.set_figwidth(width)
    figure.savefig(filepath, format=format, dpi=dpi)
    logger.info("Figure saved to '%s'", filepath)
