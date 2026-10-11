"""
This module defines studies: sets of simulations which modify a setting or
parameter to determine the impact on laptime or simulation behaviour.
"""

import logging
from collections.abc import Generator
from typing import Annotated

from pydantic import BeforeValidator
from rich import progress

from usmlap.core.library import Serialisable
from usmlap.core.nested_dict import merge_dicts
from usmlap.io.filemap import SimGroupFileMap, StudyFileMap
from usmlap.io.sim_folder import get_unique_filepath
from usmlap.simulation.settings import SimSettings
from usmlap.simulation.simulation import run_simulation
from usmlap.simulation.sweep import SweepDefinition, generate_sweep_definition

logger = logging.getLogger(__name__)


class Study(Serialisable):
    """A set of simulations sweeping a range of sim settings."""

    study_name: str
    base_settings: SimSettings
    sweep: Annotated[
        SweepDefinition, BeforeValidator(generate_sweep_definition)
    ]

    def iter_settings(self) -> Generator[SimSettings]:
        base_settings = self.base_settings.model_dump()
        for changes in self.sweep:
            settings = merge_dicts(base_settings, changes, allow_new_keys=False)
            yield SimSettings.model_validate(settings)


def run_study(study: Study, filemap: StudyFileMap) -> None:
    """Run a study consisting of a set of simulations."""
    logger.info("Running study %s", study.study_name)
    study.write_file(filemap.study_file)

    for settings in progress.track(
        study.iter_settings(),
        transient=True,
        description=f"Running study '{study.study_name}'...",
    ):
        sim_filepath = get_unique_filepath(filemap.root / settings.sim_name)
        sim_filemap = SimGroupFileMap(sim_filepath)
        run_simulation(settings, sim_filemap)
