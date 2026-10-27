"""
This module defines the files associated with a laptime simulation.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

PLOT_EXTENSIONS = {".png", ".svg", ".jpg"}


@dataclass(frozen=True, slots=True)
class StudyFileMap:
    """A mapping of the files associates with a study.
    A study is a collection of simulations using different settings,
    such as a parameter sweep or a model comparison.
    """

    root: Path

    @property
    def sim_groups(self) -> Iterator[SimGroupFileMap]:
        return (
            SimGroupFileMap(subfolder)
            for subfolder in self.sims_folder.iterdir()
            if subfolder.is_dir()
        )

    @property
    def study_file(self) -> Path:
        return self.root / "study.yaml"

    @property
    def sims_folder(self) -> Path:
        return self.root / "sims"

    @property
    def plots_folder(self) -> Path:
        """The path to the study plots folder."""
        return self.root / "plots"

    def get_plots(self) -> Iterator[Path]:
        """Iterate over the plots in the plots folder."""
        return (
            file
            for file in self.plots_folder.iterdir()
            if file.suffix in PLOT_EXTENSIONS
        )


@dataclass(frozen=True, slots=True)
class SimGroupFileMap:
    """A mapping of the files associated with a sim group.
    A sim group is a collection of sims using the same vehicle,
    such as for a competition simulation.
    """

    root: Path

    @property
    def sims(self) -> Iterator[OutingFileMap]:
        return (
            OutingFileMap(subfolder)
            for subfolder in self.root.iterdir()
            if subfolder.is_dir()
        )

    @property
    def outings_by_id(self) -> dict[str, OutingFileMap]:
        return {outing.outing_id: outing for outing in self.sims}

    @property
    def settings_file(self) -> Path:
        return self.root / "settings.yaml"

    @property
    def study(self) -> StudyFileMap:
        return StudyFileMap(self.root.parents[1])

    @property
    def vehicle_file(self) -> Path:
        """The path to the vehicle file."""
        return self.root / "vehicle.json"

    @property
    def plots_folder(self) -> Path:
        """The path to the sim group plots folder."""
        return self.root / "plots"

    def get_outing(self, outing_id: str) -> OutingFileMap | None:
        return self.outings_by_id.get(outing_id)

    def get_plots(self) -> Iterator[Path]:
        """Iterate over the plots in the plots folder."""
        return (
            file
            for file in self.plots_folder.iterdir()
            if file.suffix in PLOT_EXTENSIONS
        )


@dataclass(frozen=True, slots=True)
class OutingFileMap:
    """A mapping of the files associated with a single laptime simulation."""

    root: Path

    @property
    def log_file(self) -> Path:
        """The path to the log file."""
        return self.root / "logs.log"

    @property
    def settings_file(self) -> Path:
        """The path to the outing settings file."""
        return self.root / "settings.yaml"

    @property
    def parquet_file(self) -> Path:
        """The path to the parquet file."""
        return self.root / "channels.prq"

    @property
    def plots_folder(self) -> Path:
        """The path to the sim plots folder."""
        return self.root / "plots"

    def get_plots(self) -> Iterator[Path]:
        """Iterate over the plots in the plots folder."""
        return (
            file
            for file in self.plots_folder.iterdir()
            if file.suffix in PLOT_EXTENSIONS
        )

    @property
    def sim_group(self) -> SimGroupFileMap:
        return SimGroupFileMap(self.root.parent)

    @property
    def study(self) -> StudyFileMap:
        return self.sim_group.study

    @property
    def outing_id(self) -> str:
        return self.root.stem


if __name__ == "__main__":
    root = Path(r"out\20261023012619_MassSweep")
    for sim in root.iterdir():
        if not sim.is_dir():
            continue
        print("=" * 30)
        print(sim)
        print(list(sim.iterdir()))
