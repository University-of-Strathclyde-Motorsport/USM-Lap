"""
This module models the full vehicle.
"""

from dataclasses import dataclass

from usmlap.filepath import LIBRARY_ROOT
from usmlap.utils.datatypes import FrontRear
from usmlap.utils.library import HasLibrary

from .aero import AeroPackage
from .brakes import Brakes
from .driver import Driver
from .inertia import Inertia
from .powertrain.powertrain import RWDPowertrain
from .steering import Steering
from .suspension import Suspension
from .transmission import Transmission
from .tyre.tyre_model import Tyres


@dataclass
class Metadata(object):
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


class Vehicle(HasLibrary, path=LIBRARY_ROOT / "vehicles"):
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
        return FrontRear(front_mass, 1 - front_mass)

    @property
    def aero_distribution(self) -> FrontRear[float]:
        front_aero = self.aero.front_aero_distribution
        return FrontRear(front_aero, 1 - front_aero)

    def motor_torque_to_drive_force(self, motor_torque: float) -> float:
        return motor_torque * self._overall_motor_scaling

    def traction_force_to_motor_torque(self, traction_force: float) -> float:
        return traction_force / self._overall_motor_scaling

    def motor_speed_to_velocity(self, motor_speed: float) -> float:
        return motor_speed / self._overall_motor_scaling

    def velocity_to_motor_speed(self, velocity: float) -> float:
        return velocity * self._overall_motor_scaling
