"""Utility functions for USMLap developers."""

import logging
from pathlib import Path

import typer

from usmlap.track.track_data import (
    TRACK_LIBRARY,
    load_track_from_spreadsheet,
    save_track_data,
)

logger = logging.getLogger(__name__)

app = typer.Typer()


OUTPUT_OPTION = typer.Option(
    None, "-o", "--output-path", help="Filepath to save the data to"
)

OVERWRITE_OPTION = typer.Option(
    False, "-x", "--overwrite", help="Overwrite an existing file"
)


@app.command()
def convert_excel_track(
    excel_file: Path,
    output_path: Path | None = OUTPUT_OPTION,
    overwrite: bool = OVERWRITE_OPTION,
) -> None:
    """Convert a track from the legacy Excel format to .json."""
    if output_path is None:
        output_path = (TRACK_LIBRARY / excel_file.stem).with_suffix(".json")

    if not overwrite and output_path.exists():
        logger.error(
            (
                "%s already exists. "
                "Specify an alternative output_path or use the overwrite flag"
            ),
            output_path,
        )
        raise typer.Exit()

    track_data = load_track_from_spreadsheet(excel_file)
    save_track_data(track_data, output_path, overwrite=overwrite)
