"""
This module contains code for working with filepaths.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
LIBRARY_ROOT = PROJECT_ROOT / "appdata" / "library"
