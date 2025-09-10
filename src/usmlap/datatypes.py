"""
This module defines custom datatypes used throughout the project.
"""

from typing import Annotated, TypeVar
from pydantic import BaseModel, Field
import math

T = TypeVar("T")


class FrontRear(tuple[T, T]):
    """
    Represents a property with a front and rear value.

    Used for properties which differ on each axle of the vehicle.

    Attributes:
        front (T): Value for the front axle.
        rear (T): Value for the rear axle.
    """

    @property
    def front(self) -> T:
        return self[0]

    @property
    def rear(self) -> T:
        return self[1]

    def __str__(self) -> str:
        return f"front: {self.front}, rear: {self.rear}"


type Percentage = Annotated[float, Field(ge=0, le=1)]


class Coordinate(BaseModel):
    """
    Represents a coordinate with x, y, and z components.

    Attributes:
        x (float): x component.
        y (float): y component.
        z (float): z component (default: 0).
    """

    x: float
    y: float
    z: float = 0

    def norm(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
