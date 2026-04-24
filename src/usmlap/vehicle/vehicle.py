"""
This module models the full vehicle.
"""

from typing import Optional

from usmlap.filepath import LIBRARY_ROOT
from usmlap.utils.datatypes import FrontRear
from usmlap.utils.library import HasLibrary

from .aero import AeroPackage
from .brakes import Brakes
from .driver import Driver
from .inertia import Inertia
from .new_tyre import Tyre
from .powertrain import CellState, RWDPowertrain, StateOfCharge
from .steering import Steering
from .suspension import Suspension
from .transmission import Transmission

# from .tyre.tyre_model import Tyres


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

    print_name: str
    driver: Driver
    aero: AeroPackage
    brakes: Brakes
    inertia: Inertia
    powertrain: RWDPowertrain
    steering: Steering
    suspension: Suspension
    transmission: Transmission
    tyres: FrontRear[Tyre]
    label: str = ""
    description: str = ""
    year: Optional[int] = None

    @property
    def total_mass(self) -> float:
        return self.inertia.curb_mass + self.driver.mass

    @property
    def equivalent_mass(self) -> float:
        return self.total_mass  # TODO

    @property
    def maximum_velocity(self) -> float:
        cell_state = CellState(soc=StateOfCharge(1))
        maximum_motor_speed = self.powertrain.get_maximum_motor_speed(
            cell_state
        )
        return self.motor_speed_to_velocity(maximum_motor_speed)

    @property
    def _overall_motor_scaling(self) -> float:
        final_drive_ratio = self.transmission.final_drive_ratio
        tyre_radius = self.tyres.rear.effective_radius
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
