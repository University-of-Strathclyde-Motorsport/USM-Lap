"""
This module defines custom datatypes used throughout the project.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Annotated, Any, NamedTuple

import numpy as np
from pydantic import BaseModel, Field


class FrontRear[T](NamedTuple):
    """
    Represents a property with a front and rear value.

    Used for properties which differ on each axle of the vehicle.

    Attributes:
        front (T): Value for the front axle.
        rear (T): Value for the rear axle.
    """

    front: T
    rear: T

    def __str__(self) -> str:
        return f"front: {self.front}, rear: {self.rear}"

    def __add__(self, other: Any) -> FrontRear[T]:
        if isinstance(other, FrontRear):
            return FrontRear(*(a + b for a, b in zip(self, other)))
        elif isinstance(other, float | int):
            return FrontRear(*(a + other for a in self))
        else:
            return NotImplemented

    def __mul__(self, other: Any) -> FrontRear[T]:
        if isinstance(other, FrontRear):
            return FrontRear(*(a * b for a, b in zip(self, other)))
        elif isinstance(other, float | int):
            return FrontRear(*(a * other for a in self))
        else:
            return NotImplemented

    def normalise(self) -> FrontRear[T]:
        total = sum(self)
        if not isinstance(total, float | int):
            return NotImplemented
        return self * (1 / total)


class FourCorner[T](NamedTuple):
    """
    Represents a property with values for each corner of the vehicle.

    Attributes:
        front_left (T): Value for the front left corner.
        front_right (T): Value for the front right corner.
        rear_left (T): Value for the rear left corner.
        rear_right (T): Value for the rear right corner.
    """

    front_left: T
    front_right: T
    rear_left: T
    rear_right: T

    @property
    def fl(self) -> T:
        return self.front_left

    @property
    def fr(self) -> T:
        return self.front_right

    @property
    def rl(self) -> T:
        return self.rear_left

    @property
    def rr(self) -> T:
        return self.rear_right

    def __str__(self) -> str:
        return (
            f"FL: {self.front_left}"
            f"FR: {self.front_right}"
            f"RL: {self.rear_left}"
            f"RR: {self.rear_right}"
        )

    def __add__(self, other: Any) -> FourCorner[T]:
        if isinstance(other, FourCorner):
            return FourCorner(*(a + b for a, b in zip(self, other)))
        elif isinstance(other, float | int):
            return FourCorner(*(a + other for a in self))
        else:
            return NotImplemented

    def __mul__(self, other: Any) -> FourCorner[T]:
        if isinstance(other, FourCorner):
            return FourCorner(*(a * b for a, b in zip(self, other)))
        elif isinstance(other, float | int):
            return FourCorner(*(a * other for a in self))
        else:
            return NotImplemented


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


@dataclass
class Vector3(object):
    """
    Represents a 3D vector with x, y, and z components.

    Attributes:
        x (float): x component.
        y (float): y component.
        z (float): z component.
    """

    x: float = 0
    y: float = 0
    z: float = 0

    def __array__(self, dtype: np.dtype | None = None) -> np.ndarray:
        if dtype:
            return np.array([self.x, self.y, self.z], dtype=dtype)
        else:
            return np.array([self.x, self.y, self.z])


# @dataclass
# class RotationMatrix(object):
#     """
#     Represents a rotation around the x, y, and z axes.

#     Attributes:
#         roll (float): Rotation around the x axis.
#         pitch (float): Rotation around the y axis.
#         yaw (float): Rotation around the z axis.
#     """

#     roll: float = 0
#     pitch: float = 0
#     yaw: float = 0

#     def __array__(self) -> np.ndarray:
#         return np.array(
#             [
#                 [
#                     cos(self.pitch),
#                     -sin(self.roll) * sin(self.pitch),
#                     -cos(self.roll) * sin(self.pitch),
#                 ],
#                 [0, cos(self.roll), -sin(self.roll)],
#                 [
#                     sin(self.pitch),
#                     sin(self.roll) * cos(self.pitch),
#                     cos(self.roll) * cos(self.pitch),
#                 ],
#             ]
#         )
