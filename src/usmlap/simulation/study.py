"""
This module defines studies: sets of simulations which modify a setting or
parameter to determine the impact on laptime or simulation behaviour.
"""

import logging
from collections.abc import Generator
from typing import Annotated

from pydantic import BeforeValidator

from usmlap.core.library import Serialisable
from usmlap.core.nested_dict import merge_dicts
from usmlap.plot.studies import StudyPlots
from usmlap.simulation.settings import SimSettings
from usmlap.simulation.sweep import SweepDefinition, generate_sweep_definition

logger = logging.getLogger(__name__)


class Study(Serialisable):
    """A set of simulations sweeping a range of sim settings."""

    study_name: str
    base_settings: SimSettings
    sweep: Annotated[
        SweepDefinition, BeforeValidator(generate_sweep_definition)
    ]
    plots: StudyPlots

    def iter_settings(self) -> Generator[SimSettings]:
        base_settings = self.base_settings.model_dump()
        for changes in self.sweep:
            settings = merge_dicts(base_settings, changes, allow_new_keys=False)
            yield SimSettings.model_validate(settings)
