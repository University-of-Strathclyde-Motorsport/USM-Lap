"""This module contains functions to test-load settings files."""

import logging
from pathlib import Path

from rich.progress import Progress

from usmlap.core.library import Serialisable
from usmlap.core.registry import Registry
from usmlap.plot.config.scatter import ScatterConfig
from usmlap.plot.config.waveform import WaveformConfig
from usmlap.simulation.settings import OutingSettings
from usmlap.simulation.study import Study
from usmlap.track.track_data import TrackData
from usmlap.vehicle.aero import AeroPackage
from usmlap.vehicle.brakes import (
    BrakeCaliper,
    BrakeDisc,
    BrakePad,
    MasterCylinder,
)
from usmlap.vehicle.driver import Driver
from usmlap.vehicle.powertrain.accumulator import (
    Accumulator,
    ThermalDerateCurve,
)
from usmlap.vehicle.powertrain.cell import Cell
from usmlap.vehicle.powertrain.motor import Motor
from usmlap.vehicle.tyres import Tyre
from usmlap.vehicle.vehicle import Vehicle

logger = logging.getLogger(__name__)


LoadableModelRegistry = Registry[str, type[Serialisable]]()
LoadableModelRegistry.register("vehicle", Vehicle)
LoadableModelRegistry.register("study", Study)
LoadableModelRegistry.register("outing", OutingSettings)
LoadableModelRegistry.register("waveform", WaveformConfig)
LoadableModelRegistry.register("scatter", ScatterConfig)


def test_load(
    model: type[Serialisable], filepath: Path, *, quiet: bool = False
) -> bool:
    """Attempt to load a model from a file."""
    try:
        model.from_file(filepath)
        if not quiet:
            logger.info("Successfully loaded '%s'", filepath)
        return True
    except Exception:
        logger.error("Failed to load '%s'", filepath, exc_info=not quiet)
        return False


MODELS_BY_DIR: dict[Path, type[Serialisable]] = {
    Path(r"data/vehicles"): Vehicle,
    Path(r"data/tracks"): TrackData,
    Path(r"data/drivers"): Driver,
    Path(r"data/bms/thermal_derate"): ThermalDerateCurve,
    Path(r"data/components/accumulators"): Accumulator,
    Path(r"data/components/aero_packages"): AeroPackage,
    Path(r"data/components/brake_calipers"): BrakeCaliper,
    Path(r"data/components/brake_discs"): BrakeDisc,
    Path(r"data/components/brake_pads"): BrakePad,
    Path(r"data/components/cells"): Cell,
    Path(r"data/components/master_cylinders"): MasterCylinder,
    Path(r"data/components/motors"): Motor,
    Path(r"data/components/tyres"): Tyre,
    Path(r"sims/studies"): Study,
    Path(r"sims/outings"): OutingSettings,
    Path(r"plots/waveform"): WaveformConfig,
    Path(r"plots/scatter"): ScatterConfig,
}

_TEST_LOAD_SUFFIXES: set[str] = {".json", ".yaml"}


def test_load_all() -> None:

    with Progress(transient=True) as progress:
        task = progress.add_task("Loading models...", total=len(MODELS_BY_DIR))

        for folder, model in sorted(MODELS_BY_DIR.items()):
            progress.update(task, description=f"Loading models from '{folder}'")

            file_count = 0
            success_count = 0

            for file in folder.iterdir():
                if file.is_dir() or file.suffix not in _TEST_LOAD_SUFFIXES:
                    continue
                file_count += 1
                success = test_load(model, file, quiet=True)
                if success:
                    success_count += 1

            success_ratio = success_count / file_count if file_count > 0 else 1
            logger.info(
                "%g%% (%i/%i) files loaded from '%s'",
                success_ratio * 100,
                success_count,
                file_count,
                folder,
            )
            progress.update(task, advance=1)
