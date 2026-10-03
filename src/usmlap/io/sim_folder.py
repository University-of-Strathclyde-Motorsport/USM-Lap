"""
This module creates a folder structure for a laptime simulation.
"""

import logging
from datetime import UTC, datetime
from pathlib import Path

from usmlap.core.filepath import OUTPUT_ROOT

logger = logging.getLogger(__name__)

MAX_FOLDER_SUFFIX = 999


def make_new_sim_folder(root: Path = OUTPUT_ROOT, sim_name: str = "") -> Path:
    """Create a new folder for a laptime simulation."""
    timestamp = datetime.now(tz=UTC).strftime("%Y%m%d%H%M%S")
    base_name = "_".join([timestamp, sim_name.replace(" ", "_")]).strip("_")
    folder = get_unique_folder(root, base_name)
    folder.mkdir(parents=True, exist_ok=False)
    logger.info(f"Created simulation folder '{folder}'")
    return folder


def get_unique_folder(root: Path, base_name: str) -> Path:
    """Make a unique name for a folder by appending a number if necessary."""
    folder = root / base_name
    if not folder.exists():
        return folder

    for i in range(1, MAX_FOLDER_SUFFIX + 1):
        folder = root / f"{base_name}_{i:>03}"
        if not folder.exists():
            return folder

    raise FileExistsError(
        f"Could not create a unique folder name for {base_name} in {root} "
        f"after {MAX_FOLDER_SUFFIX} attempts."
    )
