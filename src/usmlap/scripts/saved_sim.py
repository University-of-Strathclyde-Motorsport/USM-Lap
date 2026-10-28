"""
This script runs a simulation which is saved to disk.
"""

from pathlib import Path

from usmlap.core.filepath import OUTPUT_ROOT
from usmlap.io.filemap import SimFileMap
from usmlap.simulation.settings import SimSettings
from usmlap.simulation.simulation import run_simulation


def main() -> None:  # noqa: S1720
    settings = SimSettings.from_file(Path(r"sims/basic_simulation.yaml"))
    filemap = SimFileMap(OUTPUT_ROOT / "test_sim")
    run_simulation(settings, filemap)


if __name__ == "__main__":
    main()
