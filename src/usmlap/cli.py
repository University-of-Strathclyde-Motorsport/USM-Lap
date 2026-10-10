"""
This module provides a command-line interface for running simulations.
"""

from pathlib import Path

import typer

from usmlap.core.filepath import OUTPUT_ROOT
from usmlap.io.filemap import SimGroupFileMap, StudyFileMap
from usmlap.io.sim_folder import make_timestamped_folder
from usmlap.simulation.settings import SimSettings
from usmlap.simulation.simulation import run_simulation
from usmlap.simulation.study import Study, run_study

app = typer.Typer()


@app.command()
def simulate(yaml_path: Path, output_dir: Path = OUTPUT_ROOT) -> None:
    """Run a simulation from a .yaml file."""
    settings = SimSettings.from_yaml(yaml_path)
    output_path = make_timestamped_folder(output_dir, settings.sim_name)
    filemap = SimGroupFileMap(output_path)
    run_simulation(settings, filemap)


@app.command()
def study(yaml_path: Path, output_dir: Path = OUTPUT_ROOT) -> None:
    """Run a study from a .yaml file."""
    study = Study.from_yaml(yaml_path)
    output_path = make_timestamped_folder(output_dir, study.study_name)
    filemap = StudyFileMap(output_path)
    run_study(study, filemap)
