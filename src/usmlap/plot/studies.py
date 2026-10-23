"""
This module plots charts of multiple sweeps in a study.
"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from usmlap.core.library import Serialisable
from usmlap.core.nested_dict import KeyPath, get_nested_value
from usmlap.io.filemap import StudyFileMap
from usmlap.io.parquet import read_parquet
from usmlap.simulation.settings import SimSettings


class StudyConfig(Serialisable):
    """Configuration options for a study plot."""

    title: str
    outing_id: str
    x_value: KeyPath
    y_value: str


def plot_study_bar_chart(study: StudyFileMap, config: StudyConfig) -> Figure:
    """Create a bar chart."""

    fig, ax = plt.subplots(layout="constrained")

    sim_settings = [
        SimSettings.from_file(sim_group.settings_file).as_dict()
        for sim_group in study.sim_groups
    ]

    # x_values = [
    #     get_nested_value(settings, config.x_value, float)
    #     for settings in sim_settings
    # ]

    # solutions = [read_parquet(sim) for sim in study.sim_groups]
    # laptimes =

    return fig
