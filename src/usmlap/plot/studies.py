"""
This module plots charts of multiple sweeps in a study.
"""

from pathlib import Path
from typing import Annotated

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from pydantic import BeforeValidator, ConfigDict

from usmlap.core.colour import HexColour
from usmlap.core.library import Serialisable
from usmlap.core.nested_dict import KeyPath, get_nested_value, parse_keypath
from usmlap.io.filemap import OutingFileMap, StudyFileMap
from usmlap.io.parquet import read_parquet
from usmlap.simulation.settings import SimSettings


class StudyConfig(Serialisable):
    """Configuration options for a study plot."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    title: str | None = None
    outing_id: str
    colour: HexColour = HexColour("#003366")
    x_value: Annotated[KeyPath, BeforeValidator(parse_keypath)]
    y_value: str
    x_label: str | None = None
    y_label: str | None = None


def plot_study_line_chart(study: StudyFileMap, config: StudyConfig) -> Figure:
    """Create a bar chart."""

    fig, ax = plt.subplots(layout="constrained")

    sim_settings = [
        SimSettings.from_file(sim_group.settings_file).as_dict()
        for sim_group in study.sim_groups
    ]

    x_values = [
        get_nested_value(settings, config.x_value, float)
        for settings in sim_settings
    ]

    outings = [sim.get_outing(config.outing_id) for sim in study.sim_groups]
    laptime = [_get_laptime(outing) for outing in outings]

    ax.plot(x_values, laptime, color=config.colour, marker="o")

    if config.x_label is not None:
        ax.set_xlabel(config.x_label)

    if config.y_label is not None:
        ax.set_ylabel(config.y_label)

    if config.title is not None:
        ax.set_title(config.title)

    ax.grid(True)
    return fig


def _get_laptime(outing: OutingFileMap | None) -> np.float64:
    """Get the laptime for an outing."""
    if outing is None:
        return np.float64(np.nan)
    solution = read_parquet(outing.parquet_file)
    return solution.get_laptime()


if __name__ == "__main__":
    study = StudyFileMap(Path(r"out/20261023012619_MassSweep"))
    config = StudyConfig(
        title="Mass Sensitivity",
        outing_id="autocross",
        colour="#003366",
        x_value="vehicle.parameters.inertia.curb_mass",
        y_value="laptime",
        x_label="Curb Mass (kg)",
        y_label="Laptime (s)",
    )
    fig = plot_study_line_chart(study, config)
    plt.show()
