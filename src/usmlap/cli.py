"""
This module provides a command-line interface for running simulations.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import typer

from usmlap.core.filepath import OUTPUT_ROOT
from usmlap.io.filemap import OutingFileMap, SimFileMap, StudyFileMap
from usmlap.io.parquet import read_parquet
from usmlap.io.sim_folder import make_timestamped_folder
from usmlap.io.test_load import LoadableModelRegistry, test_load, test_load_all
from usmlap.plot.config.waveform import WaveformConfig
from usmlap.plot.plots.waveform import plot_waveform
from usmlap.plot.study_plots import generate_study_plots
from usmlap.simulation.settings import SimSettings
from usmlap.simulation.simulation import run_simulation, run_study
from usmlap.simulation.study import Study

app = typer.Typer()


@app.command()
def simulate(yaml_path: Path, output_dir: Path = OUTPUT_ROOT) -> None:
    """Run a simulation from a .yaml file."""
    settings = SimSettings.from_file(yaml_path)
    output_path = make_timestamped_folder(output_dir, settings.sim_name)
    filemap = SimFileMap(output_path)
    run_simulation(settings, filemap)


@app.command()
def study(yaml_path: Path, output_dir: Path = OUTPUT_ROOT) -> None:
    """Run a study from a .yaml file."""
    study = Study.from_file(yaml_path)
    output_path = make_timestamped_folder(output_dir, study.study_name)
    filemap = StudyFileMap(output_path)
    run_study(study, filemap)


@app.command()
def load(model: str, filepath: Path) -> None:
    """Attempt to load an object from a file."""
    model_type = LoadableModelRegistry.get(model)
    test_load(model_type, filepath)


@app.command()
def load_all() -> None:
    """Test load objects from all files."""
    test_load_all()


@app.command()
def waveform(simulation: Path, config_file: Path) -> None:
    """Generate a waveform plot of a simulation."""
    filemap = OutingFileMap(simulation)
    data = read_parquet(filemap.parquet_file)
    plot_waveform(data, WaveformConfig.from_file(config_file))
    plt.show()


@app.command()
def study_plots(filepath: Path) -> None:
    """Generate all plots for a study."""
    filemap = StudyFileMap(filepath)
    generate_study_plots(filemap)
