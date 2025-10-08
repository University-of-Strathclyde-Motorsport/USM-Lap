"""
This module models the full vehicle.
"""

from .common import Subsystem
from .brakes import Brakes
from .powertrain.powertrain import RWDPowertrain
from .steering import Steering
from .suspension import Suspension
from .transmission import Transmission


class Vehicle(Subsystem):
    """
    The full vehicle.

    Attributes:
        brakes (Brakes): The brakes of the vehicle.
        powertrain (RWDPowertrain): The powertrain of the vehicle.
        steering (Steering): The steering of the vehicle.
        suspension (Suspension): The suspension of the vehicle.
        transmission (Transmission): The transmission of the vehicle.
    """

    brakes: Brakes
    powertrain: RWDPowertrain
    steering: Steering
    suspension: Suspension
    transmission: Transmission
