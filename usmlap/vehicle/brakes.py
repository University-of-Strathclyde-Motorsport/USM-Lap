from .component import Component


class MasterCylinder(Component):
    def __init__(self, piston_diameter: float | None = None):
        self.piston_diameter = piston_diameter


class BrakeCaliper(Component):
    def __init__(
        self,
        piston_count: int | None = None,
        piston_diameter: float | None = None,
    ):
        self.piston_count = piston_count
        self.piston_diameter = piston_diameter


class BrakeDisc(Component):
    def __init__(self, outer_diameter: float | None = None):
        self.outer_diameter = outer_diameter


class BrakePad(Component):
    def __init__(
        self,
        height: float | None = None,
        coefficient_of_friction: float | None = None,
    ):
        self.height = height
        self.coefficient_of_friction = coefficient_of_friction


class BrakeLine(Component):
    def __init__(
        self,
        cylinder: MasterCylinder = MasterCylinder(),
        caliper: BrakeCaliper = BrakeCaliper(),
        disc: BrakeDisc = BrakeDisc(),
        pad: BrakePad = BrakePad(),
    ):
        self.cylinder = cylinder
        self.caliper = caliper
        self.disc = disc
        self.pad = pad
