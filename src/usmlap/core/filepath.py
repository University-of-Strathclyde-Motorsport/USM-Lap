"""
This module contains code for working with filepaths.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[3]
CONFIG_ROOT = PROJECT_ROOT / "config"
PLOTS_ROOT = PROJECT_ROOT / "plots"
LIBRARY_ROOT = PROJECT_ROOT / "data"
TEMPORARY_ROOT = PROJECT_ROOT / "tmp"
OUTPUT_ROOT = PROJECT_ROOT / "out"
SIMS_ROOT = PROJECT_ROOT / "sims"
