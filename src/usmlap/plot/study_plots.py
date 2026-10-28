"""This module generates plots of a study."""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from usmlap.core.filepath import PLOTS_ROOT
from usmlap.core.nested_dict import get_nested_value
from usmlap.io.filemap import OutingFileMap, StudyFileMap
from usmlap.io.parquet import read_parquet
from usmlap.io.plots import save_figure
from usmlap.plot.config.waveform import WaveformConfig
from usmlap.plot.plots.waveform import plot_waveform
from usmlap.plot.studies import StudyLineConfig, StudyWaveform
from usmlap.simulation.settings import SimSettings
from usmlap.simulation.study import Study


def generate_study_plots(study: StudyFileMap) -> None:
    """Generate all the plots for a study."""
    plot_settings = Study.from_file(study.study_file).plots
    for line_config in plot_settings.line:
        plot_study_line_chart(study, line_config)
    for waveform_config in plot_settings.waveform:
        fig = plot_study_waveform(study, waveform_config)
        save_figure(
            fig, study.plots_folder / "waveform" / waveform_config.config
        )


def plot_study_waveform(study: StudyFileMap, config: StudyWaveform) -> Figure:
    """Plot a waveform of a set of sims in a study."""
    outings = [sim.get_outing(config.outing_id) for sim in study.sim_groups]
    outings = [outing for outing in outings if outing is not None]
    data = [read_parquet(outing.parquet_file) for outing in outings]
    #  TODO: this is messy, i don't like it
    config_file = (PLOTS_ROOT / "waveform" / config.config).with_suffix(".yaml")
    return plot_waveform(data, WaveformConfig.from_file(config_file))


def plot_study_line_chart(
    study: StudyFileMap, config: StudyLineConfig
) -> Figure:
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
