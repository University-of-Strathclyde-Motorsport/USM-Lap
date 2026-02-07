"""
This module contains definitions of physical units and quantities.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class Quantity(Enum):
    """
    Enumeration of physical quantities.
    """

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

    def __init__(self, name: str, quantity: Quantity, symbol: str) -> None:
        self.print_name = name
        self.quantity = quantity
        self.symbol = symbol

    METER = "meter", Quantity.LENGTH, "m"
    SECOND = "second", Quantity.TIME, "s"
    KILOGRAM = "kilogram", Quantity.MASS, "kg"
    RADIAN = "radian", Quantity.ANGLE, "rad"
    METER_PER_SECOND = "meter per second", Quantity.VELOCITY, "m/s"
    METER_PER_SECOND_SQUARED = (
        "meter per second squared",
        Quantity.ACCELERATION,
        "m/s^2",
    )
    NEWTON = "newton", Quantity.FORCE, "N"
    NEWTON_METER = "newton meter", Quantity.TORQUE, "Nm"
    JOULE = "joule", Quantity.ENERGY, "J"
    WATT = "watt", Quantity.POWER, "W"
