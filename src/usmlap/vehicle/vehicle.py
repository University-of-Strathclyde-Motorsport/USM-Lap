"""
This module models the full vehicle.
"""

from .common import Subsystem
from .driver import Driver
from .aero import AeroPackage
from .brakes import Brakes
from .inertia import Inertia
from .powertrain.powertrain import RWDPowertrain
from .steering import Steering
from .suspension import Suspension
from .transmission import Transmission
from .tyre.tyre_model import Tyres


class Metadata(Subsystem):
    """
    Metadata for a vehicle.

    Attributes:
        name (str): The name of the vehicle.
        year (int): The year the vehicle was built.
        description (str): A description of the vehicle (default = "").
    """

    name: str
    year: int
    description: str = ""


class Vehicle(Subsystem):
    """
    The full vehicle.

    Attributes:
        metadata (Metadata): The metadata of the vehicle.
        driver (Driver): The driver of the vehicle.
        aero (AeroPackage): The aerodynamic package of the vehicle.
        brakes (Brakes): The brakes of the vehicle.
        powertrain (RWDPowertrain): The powertrain of the vehicle.
        inertia (Inertia): The inertia properties of the vehicle.
        steering (Steering): The steering of the vehicle.
        suspension (Suspension): The suspension of the vehicle.
        transmission (Transmission): The transmission of the vehicle.
        tyres (Tyres): The tyres of the vehicle.
    """

    metadata: Metadata
    driver: Driver
    aero: AeroPackage
    brakes: Brakes
    inertia: Inertia
    powertrain: RWDPowertrain
    steering: Steering
    suspension: Suspension
    transmission: Transmission
    tyres: Tyres
