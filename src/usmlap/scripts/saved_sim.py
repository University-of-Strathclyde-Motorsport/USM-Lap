"""
This script runs a simulation which is saved to disk.
"""

from pathlib import Path

from usmlap.simulation.settings import SimSettings
from usmlap.simulation.simulation import run_simulation


def main() -> None:  # noqa: S1720
    settings = SimSettings.from_yaml(Path(r"sims/basic_simulation.yaml"))
    run_simulation(settings)


if __name__ == "__main__":
    main()
