# """
# This module contains definitions of physical units and quantities.
# """

# from __future__ import annotations

# from dataclasses import InitVar, dataclass, field
# from enum import Enum
# from math import pi

# from usmlap.filepath import LIBRARY_ROOT
# from usmlap.utils.library import ArrayLibrary


# class QuantityError(Exception):
#     """Base exception for quantity errors."""

#     pass


# @dataclass(frozen=True, slots=True)
# class IncompatibleQuantityError(QuantityError):
#     """Raised when a mathematical operation is attempted on incompatible quantities."""

#     operation: str
#     quantities: tuple[Quantity, ...]

#     def __str__(self) -> str:
#         quantity_strs = ", ".join(str(q) for q in self.quantities)
#         return f"Cannot perform {self.operation} due to incompatible quantities: {quantity_strs}"


# type QuantityVector = tuple[int, int, int, int, int, int, int]


# @dataclass
# class Quantity(ArrayLibrary, path=LIBRARY_ROOT / "units" / "quantities.json"):
#     """
#     Represents a physical quantity.
#     """

#     print_name: str = field(compare=False)
#     time: int = 0
#     length: int = 0
#     mass: int = 0
#     current: int = 0
#     temperature: int = 0
#     amount: int = 0
#     luminous_intensity: int = 0

#     def as_vector(self) -> QuantityVector:
#         return (
#             self.time,
#             self.length,
#             self.mass,
#             self.current,
#             self.temperature,
#             self.amount,
#             self.luminous_intensity,
#         )

#     @classmethod
#     def from_vector(
#         cls, vector: QuantityVector, *, print_name: str = ""
#     ) -> Quantity:
#         return cls(
#             print_name=print_name,
#             time=vector[0],
#             length=vector[1],
#             mass=vector[2],
#             current=vector[3],
#             temperature=vector[4],
#             amount=vector[5],
#             luminous_intensity=vector[6],
#         )

#     def __str__(self) -> str:
#         return self.print_name

#     def __add__(self, other: Quantity) -> Quantity:
#         if self != other:
#             raise IncompatibleQuantityError("addition", (self, other))
#         return self

#     def __sub__(self, other: Quantity) -> Quantity:
#         if self != other:
#             raise IncompatibleQuantityError("subtraction", (self, other))
#         return self

#     def __mul__(self, other: Quantity) -> Quantity:
#         vector_1 = self.as_vector()
#         vector_2 = other.as_vector()
#         result_vector = tuple(v1 + v2 for v1, v2 in zip(vector_1, vector_2))
#         return Quantity.from_vector(result_vector)

#     def __truediv__(self, other: Quantity) -> Quantity:
#         vector_1 = self.as_vector()
#         vector_2 = other.as_vector()
#         result_vector = tuple(v1 - v2 for v1, v2 in zip(vector_1, vector_2))
#         return Quantity.from_vector(result_vector)


# # class QuantityLibrary(Quantity, Enum):
# #     """A library of known physical quantities."""

# #     # def __new__(cls, quantity: Quantity) -> QuantityLibrary:
# #     #     # value = len(cls.__members__) + 1
# #     #     obj = object.__new__(cls)
# #     #     obj._value_ = quantity
# #     #     return obj

# #     def __init__(self, quantity: Quantity) -> None:
# #         for key in quantity.__annotations__.keys():
# #             value = getattr(quantity, key)
# #             setattr(self, key, value)

# #     UNITLESS = Quantity("unitless")
# #     # Kinematics
# #     TIME = Quantity("time", time=1)
# #     LENGTH = Quantity("length", length=1)
# #     CURVATURE = Quantity("curvature", length=-1)
# #     VELOCITY = Quantity("velocity", length=1, time=-1)
# #     ACCELERATION = Quantity("acceleration", length=1, time=-2)
# #     ANGLE = Quantity("angle")
# #     ANGULAR_VELOCITY = Quantity("angular velocity", time=-1)
# #     ANGULAR_ACCELERATION = Quantity("angular acceleration", time=-2)
# #     # Kinetics
# #     MASS = Quantity("mass", mass=1)
# #     FORCE = Quantity("force", mass=1, length=1, time=-2)
# #     TORQUE = Quantity("torque", mass=1, length=2, time=-2)
# #     ENERGY = Quantity("energy", mass=1, length=2, time=-2)
# #     POWER = Quantity("power", mass=1, length=2, time=-3)
# #     TEMPERATURE = Quantity("temperature", temperature=1)
# #     # Electrical
# #     CURRENT = Quantity("current", current=1)
# #     CHARGE = Quantity("charge", current=1, time=1)
# #     VOLTAGE = Quantity("voltage", mass=1, length=2, time=-3, current=-1)
# #     RESISTANCE = Quantity("resistance", mass=1, length=2, time=-3, current=-2)


# # @dataclass(frozen=True, slots=True)
# @dataclass
# class Unit(ArrayLibrary, path=LIBRARY_ROOT / "units" / "units.json"):
#     """
#     Represents a physical unit.
#     """

#     name: str
#     quantity: InitVar[str]
#     quantity: Quantity = Quantity.get_item("unitless")
#     symbol: str = ""
#     conversion_factor: float = 1

#     def __post_init__(self, quantity_name: str) -> None:
#         quantity = Quantity.get_item(quantity_name)
#         object.__setattr__(self, "quantity", quantity)

#     def convert(self, value: float) -> float:
#         return value / self.conversion_factor

#     def __str__(self) -> str:
#         return self.symbol

#     def format_label(self, label: str) -> str:
#         """Format a label for a plot with the unit's symbol in brackets.

#         Example:
#             >>> UnitLibrary.METER_PER_SECOND.format_label("Velocity")
#             "Velocity (m/s)"
#             >>> UnitLibrary.UNITLESS.format_label("Lap Number")
#             "Lap Number"
#         """
#         if not self.symbol:
#             return label
#         return f"{label} ({self.symbol})"


# # class UnitLibrary(Unit, Enum):
# #     """
# #     Enumeration of physical units.

# #     Attributes:
# #         print_name (str): The name of the unit.
# #         quantity (QuantityLibrary): The physical quantity the unit represents.
# #         symbol (str): The symbol of the unit.
# #     """

# #     def __init__(self, unit: Unit) -> None:
# #         for key in unit.__annotations__.keys():
# #             value = getattr(unit, key)
# #             setattr(self, key, value)

# #     UNITLESS = Unit("unitless", Quantity.get_item("unitless"), "")
# #     METER = Unit("meter", Quantity.get_item("length"), "m")
# #     PER_METER = Unit("per meter", Quantity.get_item("curvature"), "1/m")
# #     SECOND = Unit("second", Quantity.get_item("time"), "s")
# #     MILLISECOND = Unit("millisecond", Quantity.get_item("time"), "ms", 1e-3)
# #     KILOGRAM = Unit("kilogram", Quantity.get_item("mass"), "kg")
# #     RADIAN = Unit("radian", Quantity.get_item("angle"), "rad")
# #     RADIANS_PER_SECOND = Unit(
# #         "radians per second", Quantity.get_item("angular velocity"), "rad/s"
# #     )
# #     RPM = Unit(
# #         "revolutions per minute",
# #         Quantity.get_item("angular velocity"),
# #         "rpm",
# #         pi / 30,
# #     )
# #     METER_PER_SECOND = Unit(
# #         "meter per second", Quantity.get_item("velocity"), "m/s"
# #     )
# #     KILOMETER_PER_HOUR = Unit(
# #         "kilometer per hour", Quantity.get_item("velocity"), "km/h", 1 / 3.6
# #     )
# #     MILE_PER_HOUR = Unit(
# #         "mile per hour", Quantity.get_item("velocity"), "mph", 0.44704
# #     )
# #     METER_PER_SECOND_SQUARED = Unit(
# #         "meter per second squared", Quantity.get_item("acceleration"), "m/s^2"
# #     )
# #     G = Unit("g", Quantity.get_item("acceleration"), "g", 9.81)
# #     NEWTON = Unit("newton", Quantity.get_item("force"), "N")
# #     NEWTON_METER = Unit("newton meter", Quantity.get_item("torque"), "Nm")
# #     JOULE = Unit("joule", Quantity.get_item("energy"), "J")
# #     MEGAJOULE = Unit("megajoule", Quantity.get_item("energy"), "MJ", 1e6)
# #     KILOWATT_HOUR = Unit(
# #         "kilowatt hour", Quantity.get_item("energy"), "kWh", 3.6e6
# #     )
# #     WATT = Unit("watt", Quantity.get_item("power"), "W")
# #     KILOWATT = Unit("kilowatt", Quantity.get_item("power"), "kW", 1e3)
# #     DEGREE_CELSIUS = Unit(
# #         "degree celsius", Quantity.get_item("temperature"), "°C"
# #     )
# #     AMPERE = Unit("ampere", Quantity.get_item("current"), "A")
# #     PERCENTAGE = Unit("percentage", Quantity.get_item("unitless"), "%", 0.01)
