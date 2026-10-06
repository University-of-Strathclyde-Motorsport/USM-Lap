"""
This module models the environment in which the vehicle is simulated."""

from pydantic import BaseModel, Field


class EnvironmentSettings(BaseModel):
    """Environmental variables for the simulation.

    Attributes:
        gravity (float): Acceleration due to gravity (default = 9.81).
        air_density (float): The density of the air (default = 1.225).
        ambient_temperature (float): The ambient air temperature (default = 25).
    """

    gravity: float = 9.81
    air_density: float = Field(ge=1, default=1.225)
    ambient_temperature: float = 32
