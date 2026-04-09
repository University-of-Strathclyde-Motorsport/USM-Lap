"""
This module models the full vehicle.
"""

import os
from typing import Literal

import numpy as np

from usmlap import filepath
from usmlap.utils.datatypes import FrontRear

from .aero import AeroPackage
from .brakes import Brakes
from .common import Subsystem
from .driver import Driver
from .inertia import Inertia
from .powertrain.powertrain import RWDPowertrain
from .steering import Steering
from .suspension import Suspension
from .transmission import Transmission
from .tyre.tyre_model import Tyres

VEHICLE_LIBRARY = filepath.LIBRARY_ROOT / "vehicles"
AVAILABLE_VEHICLES = os.listdir(VEHICLE_LIBRARY)


# type FrontRear = np.ndarray[tuple[Literal[1], Literal[2]], np.dtype[np.float64]]


class Metadata(Subsystem):
    """
    Metadata for a vehicle.

    Attributes:
        print_name (str): The name of the vehicle.
        year (int): The year the vehicle was built.
        description (str): A description of the vehicle (default = "").
    """

    print_name: str
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

    @property
    def total_mass(self) -> float:
        return self.inertia.curb_mass + self.driver.mass

    @property
    def equivalent_mass(self) -> float:
        return self.total_mass  # TODO

    @property
    def maximum_velocity(self) -> float:
        maximum_motor_speed = self.powertrain.get_maximum_motor_speed(1)
        return self.motor_speed_to_velocity(maximum_motor_speed)

    @property
    def _overall_motor_scaling(self) -> float:
        final_drive_ratio = self.transmission.final_drive_ratio
        tyre_radius = self.tyres.rear.unloaded_radius
        return final_drive_ratio / tyre_radius

    @property
    def mass_distribution(self) -> FrontRear[float]:
        front_mass = self.inertia.front_mass_distribution
        return FrontRear(front=front_mass, rear=1 - front_mass)

    @property
    def aero_distribution(self) -> FrontRear[float]:
        front_aero = self.aero.front_aero_distribution
        return FrontRear(front=front_aero, rear=1 - front_aero)

    @property
    def _long_lt_coefficient(self) -> float:
        """Longitudinal load transfer coefficient."""
        return (
            self.total_mass
            * self.suspension.centre_of_gravity_height
            / self.suspension.wheelbase
        )

    def long_load_transfer(self, acceleration: float) -> float:
        """
        Calculate the longitudinal load transfer.

        Args:
            acceleration (float): The acceleration of the vehicle.

        Returns:
            load_transfer (float): The longitudinal load transfer.
                Positive for load transfer to the front.
        """
        return -acceleration * self._long_lt_coefficient

    def motor_torque_to_drive_force(self, motor_torque: float) -> float:
        return motor_torque * self._overall_motor_scaling

    def traction_force_to_motor_torque(self, traction_force: float) -> float:
        return traction_force / self._overall_motor_scaling

    def motor_speed_to_velocity(self, motor_speed: float) -> float:
        return motor_speed / self._overall_motor_scaling

    def velocity_to_motor_speed(self, velocity: float) -> float:
        return velocity * self._overall_motor_scaling


def load_vehicle(filename: str) -> Vehicle:
    """
    Load a vehicle from the library.

    Args:
        filename (str): The name of the vehicle file.

    Returns:
        vehicle (Vehicle): The loaded vehicle.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    try:
        filepath = VEHICLE_LIBRARY / filename
        return Vehicle.from_json(filepath)
    except FileNotFoundError:
        error_message = (
            f"Unable to find '{filename}' in vehicle library. "
            f"Available vehicles: {AVAILABLE_VEHICLES}"
        )
        raise FileNotFoundError(error_message)
