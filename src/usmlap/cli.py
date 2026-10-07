"""
This module provides a command-line interface for running simulations.
"""

from pathlib import Path

import typer

from usmlap.simulation.settings import SimSettings
from usmlap.simulation.simulation import run_simulation

app = typer.Typer()


@app.command()
def hello() -> None:
    print("Hello from usmlap!")


@app.command()
def simulate(yaml_path: Path) -> None:
    settings = SimSettings.from_yaml(yaml_path)
    run_simulation(settings)
