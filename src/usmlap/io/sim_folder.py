"""
This module creates a folder structure for a laptime simulation.
"""

import logging
from datetime import UTC, datetime
from pathlib import Path

from usmlap.core.filepath import OUTPUT_ROOT

logger = logging.getLogger(__name__)

MAX_FOLDER_SUFFIX = 999


def make_timestamped_folder(root: Path = OUTPUT_ROOT, name: str = "") -> Path:
    """Create a new folder for a laptime simulation."""
    timestamp = datetime.now(tz=UTC).strftime("%Y%m%d%H%M%S")
    base_name = "_".join([timestamp, name.replace(" ", "_")]).strip("_")
    folder = get_unique_filepath(root / base_name)
    folder.mkdir(parents=True, exist_ok=False)
    logger.info(f"Created simulation folder '{folder}'")
    return folder


def get_unique_filepath(base_filepath: Path) -> Path:
    """Make a unique name for a file by appending a number if necessary."""
    if not base_filepath.exists():
        return base_filepath

    base_name = base_filepath.stem
    for i in range(1, MAX_FOLDER_SUFFIX + 1):
        filepath = base_filepath.with_stem(f"{base_name}_{i:>03}")
        if not filepath.exists():
            return filepath

    raise FileExistsError(
        f"Could not create a unique filename for {base_filepath} "
        f"after {MAX_FOLDER_SUFFIX} attempts."
    )


if __name__ == "__main__":
    test = Path(r"D:\Repositories\USM-Lap")
    new_test = test / "xyz"
    print(new_test)
    print(new_test.with_stem("tuv"))
