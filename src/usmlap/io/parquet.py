"""
This module reads and writes channels to parquet files.
"""

import logging
from pathlib import Path

import polars

from usmlap.core.types import Array1D
from usmlap.solver.solution_channels import ChannelId, SolutionDataFrame

logger = logging.getLogger(__name__)


def write_parquet(data: dict[ChannelId, Array1D], filepath: Path) -> None:
    """Write a list of channels to a parquet file."""
    logger.info("Writing %i channels to '%s'", len(data), filepath)
    polars.DataFrame(data).write_parquet(filepath)


def read_parquet(filepath: Path) -> SolutionDataFrame:
    """Read a list of channels from a parquet file."""
    df = polars.read_parquet(filepath)
    logger.info("Read %i channels from '%s'", len(df.columns), filepath)
    return SolutionDataFrame(df)
