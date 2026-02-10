"""
This module contains definitions of physical units and quantities.
"""

from __future__ import annotations

from enum import Enum
from math import pi
from typing import Any


class Quantity(Enum):
    """
    Enumeration of physical quantities.
    """

    UNITLESS = "unitless"
    TIME = "time"
    LENGTH = "length"
    CURVATURE = "curvature"
    VELOCITY = "velocity"
    ACCELERATION = "acceleration"
    ANGLE = "angle"
    ANGULAR_VELOCITY = "angular_velocity"
    ANGULAR_ACCELERATION = "angular_acceleration"
    MASS = "mass"
    FORCE = "force"
    TORQUE = "torque"
    ENERGY = "energy"
    POWER = "power"

    def __str__(self) -> str:
        return self.value


class Unit(Enum):
    """
    Enumeration of physical units.

    Attributes:
        print_name (str): The name of the unit.
        quantity (Quantity): The physical quantity the unit represents.
        symbol (str): The symbol of the unit.
    """

    def __new__(cls, *args: Any, **kwargs: Any) -> Unit:
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(
        self,
        name: str,
        quantity: Quantity,
        symbol: str,
        conversion_factor: float = 1,
    ) -> None:
        self.print_name = name
        self.quantity = quantity
        self.symbol = symbol
        self.conversion_factor = conversion_factor

    def convert(self, value: float) -> float:
        return value / self.conversion_factor

    def __str__(self) -> str:
        return self.symbol

    UNITLESS = ("unitless", Quantity.UNITLESS, "-")
    METER = ("meter", Quantity.LENGTH, "m")
    PER_METER = ("per meter", Quantity.CURVATURE, "1/m")
    SECOND = ("second", Quantity.TIME, "s")
    KILOGRAM = ("kilogram", Quantity.MASS, "kg")
    RADIAN = ("radian", Quantity.ANGLE, "rad")
    RADIANS_PER_SECOND = (
        "radians per second",
        Quantity.ANGULAR_VELOCITY,
        "rad/s",
    )
    RPM = ("revolutions per minute", Quantity.ANGULAR_VELOCITY, "rpm", pi / 30)
    METER_PER_SECOND = ("meter per second", Quantity.VELOCITY, "m/s")
    KILOMETER_PER_HOUR = (
        "kilometer per hour",
        Quantity.VELOCITY,
        "km/h",
        1 / 3.6,
    )
    MILE_PER_HOUR = ("mile per hour", Quantity.VELOCITY, "mph", 0.44704)
    METER_PER_SECOND_SQUARED = (
        "meter per second squared",
        Quantity.ACCELERATION,
        "m/s^2",
    )
    G = ("g", Quantity.ACCELERATION, "g", 9.81)
    NEWTON = ("newton", Quantity.FORCE, "N")
    NEWTON_METER = ("newton meter", Quantity.TORQUE, "Nm")
    JOULE = ("joule", Quantity.ENERGY, "J")
    MEGAJOULE = ("megajoule", Quantity.ENERGY, "MJ", 1e6)
    KILOWATT_HOUR = ("kilowatt hour", Quantity.ENERGY, "kWh", 3.6e6)
    WATT = ("watt", Quantity.POWER, "W")
    KILOWATT = ("kilowatt", Quantity.POWER, "kW", 1e3)
