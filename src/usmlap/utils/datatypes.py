"""
This module defines custom datatypes used throughout the project.
"""

import math
from dataclasses import dataclass
from typing import Annotated, TypeVar

import numpy as np
from pydantic import BaseModel, Field

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
