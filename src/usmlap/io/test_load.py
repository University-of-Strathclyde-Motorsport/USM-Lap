"""This module contains functions to test-load settings files."""

import logging
from pathlib import Path

from usmlap.core.library import LibraryLoadError, Serialisable
from usmlap.core.registry import Registry
from usmlap.plot.config.scatter import ScatterConfig
from usmlap.plot.config.waveform import WaveformConfig
from usmlap.simulation.settings import OutingSettings
from usmlap.simulation.study import Study

logger = logging.getLogger(__name__)


LoadableModelRegistry = Registry[str, type[Serialisable]]()
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
        # logger.info("Successfully loaded '%s'", filepath)
        return True
    except LibraryLoadError:
        logger.error("Failed to load '%s'", filepath, exc_info=not quiet)
        return False


MODELS_BY_DIR: dict[Path, type[Serialisable]] = {
    Path(r"sims/studies"): Study,
    Path(r"sims/outings"): OutingSettings,
    Path(r"plots/waveform"): WaveformConfig,
    Path(r"plots/scatter"): ScatterConfig,
}


def test_load_all() -> None:

    for folder, model in MODELS_BY_DIR.items():
        logger.info("Loading models from '%s'", folder)
        files = list(folder.iterdir())
        file_count = len(files)
        success_count = 0

        for file in files:
            success = test_load(model, file, quiet=True)
            if success:
                success_count += 1

        success_ratio = success_count / file_count
        logger.info(
            "%g%% (%i/%i) files loaded from '%s'",
            success_ratio * 100,
            success_count,
            file_count,
            folder,
        )
