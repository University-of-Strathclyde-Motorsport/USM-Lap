"""
This module contains code for working with filepaths.
"""

import pathlib

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.parent
LIBRARY_ROOT = PROJECT_ROOT / "appdata" / "library"
