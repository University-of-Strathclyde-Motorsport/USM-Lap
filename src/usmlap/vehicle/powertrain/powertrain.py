"""
This module models the electric powertrain of a vehicle.
"""

from abc import ABC
from pydantic.dataclasses import dataclass
from .accumulator import Accumulator
from .motor import Motor
from .motor_controller import MotorController


class Powertrain(ABC):
    """
    Abstract base class for powertrain models.
    """

    ...


@dataclass
class RWDPowertrain(Powertrain):
    """
    A single motor, rear wheel drive electric powertrain.

    Attributes:
        accumulator: The accumulator of the powertrain.
        motor: The motor of the powertrain.
        motor_controller: The motor controller of the powertrain.
    """

    accumulator: Accumulator
    motor: Motor
    motor_controller: MotorController
