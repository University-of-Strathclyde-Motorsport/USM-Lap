"""
This module models the environment in which the vehicle is simulated.
"""

from dataclasses import dataclass

GRAVITY = 9.81
AIR_DENSITY = 1.225
AMBIENT_TEMPERATURE = 32


@dataclass
class Environment(object):
    """
    Environmental variables for the simulation.

    Attributes:
        gravity (float): Acceleration due to gravity (default = 9.81).
        air_density (float): The density of the air (default = 1.225).
        ambient_temperature (float): The ambient air temperature (default = 25).
    """

    gravity: float = GRAVITY
    air_density: float = AIR_DENSITY
    ambient_temperature: float = AMBIENT_TEMPERATURE
