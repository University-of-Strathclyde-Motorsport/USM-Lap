"""
This module defines the files associated with a laptime simulation.
"""

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileMap:
    """A mapping of the files associated with a laptime simulation."""

    root: Path

    @property
    def vehicle_file(self) -> Path:
        """The path to the vehicle file."""
        return self.root / "vehicle.json"

    @property
    def settings_file(self) -> Path:
        """The path of the simulation settings."""
        return self.root / "settings.json"

    @property
    def log_file(self) -> Path:
        """The path to the log file."""
        return self.root / "logs.log"

    @property
    def plots_folder(self) -> Path:
        """The path to the plots folder."""
        return self.root / "plots"

    def get_plots(self) -> Iterator[Path]:
        """Iterate over the plots in the plots folder."""
        return self.plots_folder.glob("*.png")
