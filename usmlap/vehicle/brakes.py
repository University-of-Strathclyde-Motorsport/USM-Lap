from .common import Component, Subsystem
from utils import geometry
from datatypes import FrontRear


class MasterCylinder(Component):
    @classmethod
    def library_name(cls) -> str:
        return "master_cylinders.json"

    def __init__(self, piston_diameter: float, colour: str):
        self.piston_diameter = piston_diameter
        self.colour = colour

    def get_piston_area(self) -> float:
        return geometry.area_of_circle(self.piston_diameter)


class BrakeCaliper(Subsystem):
    def __init__(self, piston_count: int, piston_diameter: float):
        self.piston_count = piston_count
        self.piston_diameter = piston_diameter

    def get_piston_area(self) -> float:
        return self.piston_count * geometry.area_of_circle(self.piston_diameter)


class BrakeDisc(Subsystem):
    def __init__(self, outer_diameter: float):
        self.outer_diameter = outer_diameter


class BrakePad(Subsystem):
    def __init__(self, height: float, coefficient_of_friction: float):
        self.height = height
        self.coefficient_of_friction = coefficient_of_friction


class BrakeLine(Subsystem):
    def __init__(
        self,
        cylinder: str,
        caliper: BrakeCaliper,
        disc: BrakeDisc,
        pad: BrakePad,
    ):
        self.cylinder = MasterCylinder.from_library(cylinder)
        self.caliper = caliper
        self.disc = disc
        self.pad = pad

    def _area_scaling_factor(self) -> float:
        cylinder_area = self.cylinder.get_piston_area()
        caliper_area = self.caliper.get_piston_area()
        return caliper_area / cylinder_area

    def _effective_radius(self) -> float:
        return self.disc.outer_diameter - (self.pad.height / 2)

    def get_brake_pressure(self, cylinder_force: float) -> float:
        return cylinder_force / self.cylinder.get_piston_area()

    def force_to_torque(self, cylinder_force: float) -> float:
        return (
            0.5
            * cylinder_force
            * self._area_scaling_factor()
            * self.pad.coefficient_of_friction
            * self._effective_radius()
        )

    def torque_to_force(self, wheel_torque: float) -> float:
        return wheel_torque / self.force_to_torque(1)


class Brakes(Subsystem):
    def __init__(
        self,
        brake_lines: FrontRear[BrakeLine],
        pedal_ratio: float,
        front_brake_bias: float,
        regen_torque: float,
    ):
        self.brake_lines = brake_lines
        self.pedal_ratio = pedal_ratio
        self.front_brake_bias = front_brake_bias
        self.regen_torque = regen_torque

    def _get_front_brake_balance(self) -> float:
        front_multiplier = self.brake_lines.front.force_to_torque(1)
        rear_multiplier = self.brake_lines.rear.force_to_torque(1)
        return front_multiplier / (front_multiplier + rear_multiplier)
