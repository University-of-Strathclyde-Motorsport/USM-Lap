"""
This module models the environment in which the vehicle is simulated.
"""

from pydantic import BaseModel

GRAVITY = 9.81
AIR_DENSITY = 1.225


class Environment(BaseModel):
    """
    Environmental variables for the simulation.

    Attributes:
        gravity (float): Acceleration due to gravity (default = 9.81).
        air_density (float): The density of the air (default = 1.225).
    """

    gravity: float = GRAVITY
    air_density: float = AIR_DENSITY
