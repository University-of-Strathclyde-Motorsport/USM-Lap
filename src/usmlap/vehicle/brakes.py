"""
This module models the brake system of a vehicle.
"""

from .common import Component, Subsystem
from utils import geometry, proportion
from pydantic import PositiveFloat, PositiveInt
from datatypes import FrontRear, Percentage
from typing import Annotated
from annotated_types import Unit


class MasterCylinder(Component):
    """
    The master cylinder, transmitting force from the pedal to the brake line.

    Attributes:
        piston_diameter (float): The diameter of the piston.
        colour (str): The colour of the master cylinder.
        piston_area (float): The area of the piston.
    """

    piston_diameter: Annotated[PositiveFloat, Unit("m")]
    colour: str

    @property
    def piston_area(self) -> float:
        return geometry.area_of_circle(self.piston_diameter)

    @classmethod
    def library_name(cls) -> str:
        return "master_cylinders.json"


class BrakeCaliper(Component):
    """
    The brake caliper, transmitting force from the brake line to the wheel.

    Attributes:
        piston_count (int): The number of pistons in the caliper.
        piston_diameter (float): The diameter of the piston.
        piston_area (float): The total area of the pistons.
    """

    piston_count: PositiveInt
    piston_diameter: Annotated[PositiveFloat, Unit("m")]

    @property
    def piston_area(self) -> float:
        return self.piston_count * geometry.area_of_circle(self.piston_diameter)

    @classmethod
    def library_name(cls) -> str:
        return "brake_calipers.json"


class BrakeDisc(Component):
    """
    The brake disc attached to the wheel.

    Attributes:
        outer_diameter (float): The outer diameter of the brake disc.
    """

    outer_diameter: Annotated[PositiveFloat, Unit("m")]

    @classmethod
    def library_name(cls) -> str:
        return "brake_discs.json"


class BrakePad(Component):
    """
    The brake pad attached to the caliper.

    Attributes:
        height (float): The height of the brake pad.
        coefficient_of_friction (float):
            The coefficient of friction between the brake pad and brake disc.
    """

    height: Annotated[PositiveFloat, Unit("m")]
    coefficient_of_friction: PositiveFloat

    @classmethod
    def library_name(cls) -> str:
        return "brake_pads.json"


class BrakeLine(Subsystem):
    """
    An individual brake line.

    Attributes:
        cylinder (MasterCylinder): The master cylinder attached to the pedal.
        caliper (BrakeCaliper): The brake caliper attached to the wheel.
        disc (BrakeDisc): The brake disc attached to the wheel.
        pad (BrakePad): The brake pad attached to the caliper.
    """

    cylinder: MasterCylinder
    caliper: BrakeCaliper
    disc: BrakeDisc
    pad: BrakePad

    @property
    def _area_scaling_factor(self) -> float:
        """The force scaling factor between the cylinder and caliper."""
        return self.caliper.piston_area / self.cylinder.piston_area

    @property
    def _effective_radius(self) -> float:
        """The radius at which the braking force is applied to the wheel."""
        return 0.5 * (self.disc.outer_diameter - self.pad.height)

    @property
    def _force_to_torque_scaling_factor(self) -> float:
        """The ratio between braking torque and master cylinder force."""
        return (
            self._area_scaling_factor
            * self.pad.coefficient_of_friction
            * self._effective_radius
        )

    def get_brake_pressure(self, cylinder_force: float) -> float:
        """
        Calculate the pressure of the brake fluid.

        Args:
            cylinder_force (float): Force applied to the master cylinder.

        Returns:
            brake_pressure (float): Gauge pressure of the brake fluid.
        """
        return cylinder_force / self.cylinder.piston_area

    def force_to_torque(self, cylinder_force: float) -> float:
        """
        Calculate the braking torque applied to the wheel.

        Args:
            cylinder_force (float): Force applied to the master cylinder.

        Returns:
            braking_torque (float): Torque applied to the wheel.
        """
        return cylinder_force * self._force_to_torque_scaling_factor

    def torque_to_force(self, braking_torque: float) -> float:
        """
        Calculate the force required to apply a torque to the wheel.

        Args:
            braking_torque (float): Braking torque required on the wheel.

        Returns:
            cylinder_force (float): Force required on the master cylinder.
        """
        return braking_torque / self._force_to_torque_scaling_factor


class Brakes(Subsystem):
    """
    The brake system of the vehicle.

    Attributes:
        front (BrakeLine): Brake line for the front wheels.
        rear (BrakeLine): Brake line for the rear wheels.
        pedal_ratio (float): Ratio of master cylinder force to pedal force.
        front_brake_bias (float):
            Proportion of force applied to the front master cylinder
            (value between 0 and 1).
        regen_torque (float): Maximum regenerative braking torque.
    """

    front: BrakeLine
    rear: BrakeLine
    pedal_ratio: PositiveFloat
    front_brake_bias: Percentage
    regen_torque: Annotated[PositiveFloat, Unit("Nm")]

    @property
    def brake_bias(self) -> FrontRear[float]:
        """Tuple of brake biases for the front and rear wheels."""
        return FrontRear(proportion.with_complement(self.front_brake_bias))

    @property
    def brake_lines(self) -> FrontRear[BrakeLine]:
        """Tuple of front and rear brake lines."""
        return FrontRear((self.front, self.rear))

    def _get_front_brake_balance(self) -> float:
        front_multiplier = self.front.force_to_torque(1)
        rear_multiplier = self.rear.force_to_torque(1)
        return front_multiplier / (front_multiplier + rear_multiplier)

    def _get_cylinder_forces(self, pedal_force: float) -> FrontRear[float]:
        """
        Get the force applied to the front and rear master cylinders.

        Args:
            pedal_force (float): Force applied to the pedal.

        Returns:
            cylinder_forces (FrontRear[float]):
                Force applied to the master cylinders.
        """
        total_force = pedal_force * self.pedal_ratio
        return FrontRear([total_force * bias for bias in self.brake_bias])

    def pedal_force_to_wheel_torque(
        self, pedal_force: float
    ) -> FrontRear[float]:
        cylinder_forces = self._get_cylinder_forces(pedal_force)
        return FrontRear(
            brake_line.force_to_torque(force)
            for brake_line, force in zip(self.brake_lines, cylinder_forces)
        )

    def get_overall_brake_balance(self) -> FrontRear[float]:
        torques = self.pedal_force_to_wheel_torque(1)
        return FrontRear(proportion.normalise(torques))
