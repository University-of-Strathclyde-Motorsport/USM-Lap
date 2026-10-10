"""
Initialise the usmlap project.
"""

import matplotlib

from usmlap.core.log import configure_logging

configure_logging()
matplotlib.use("TkAgg")
