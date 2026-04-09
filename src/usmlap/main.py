"""
Main entry point for the program.
"""

import logging

from usmlap.utils.datatypes import FrontRear

CHANNELS = [
    "Velocity",
    "Curvature",
    "Longitudinal Acceleration",
    "Lateral Acceleration",
    "State of Charge",
]

logging.basicConfig(
    level=logging.WARN,
    format="{asctime} {levelname}: {message}",
    style="{",
    datefmt="%H:%M:%S",
)
logging.getLogger("simulation.model.point_mass").setLevel(logging.DEBUG)


a = FrontRear(1, 2)
b = FrontRear(3, 4)
print(a + b)
print(a + 1)
print(a * 2)
