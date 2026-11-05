"""This module contains type definitions used throughout the library."""

from __future__ import annotations

import math
from typing import Annotated, Any, NamedTuple

import numpy as np
from pydantic import BaseModel, Field

type Percentage = Annotated[float, Field(ge=0, le=1)]

type Array1D = np.ndarray[tuple[int], np.dtype[np.float64]]


class Coordinate(BaseModel):
    """Represents a coordinate with x, y, and z components.

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


class FrontRear[T](NamedTuple):
    """Represents a property with a front and rear value.

    Used for properties which differ on each axle of the vehicle.

    Attributes:
        front (T): Value for the front axle.
        rear (T): Value for the rear axle.

    """

    front: T
    rear: T

    def __add__(self, other: Any) -> FrontRear[T]:
        if isinstance(other, FrontRear):
            return FrontRear(*(a + b for a, b in zip(self, other, strict=True)))
        if isinstance(other, float | int):
            return FrontRear(*(a + other for a in self))
        return NotImplemented

    def __mul__(self, other: Any) -> FrontRear[T]:
        if isinstance(other, FrontRear):
            return FrontRear(*(a * b for a, b in zip(self, other, strict=True)))
        if isinstance(other, float | int):
            return FrontRear(*(a * other for a in self))
        return NotImplemented

    def normalise(self) -> FrontRear[T]:
        if not isinstance(self.front, float | int):
            return NotImplemented
        total = sum(self)
        return self * (1 / total) if total != 0 else self


class LeftRight[T](NamedTuple):
    """Represents a property with a left and right value.

    Used for properties which differ on each side of the vehicle.

    Attributes:
        left (T): Value for the left hand side.
        rear (T): Value for the right hand side.

    """

    left: T
    right: T

    def __add__(self, other: Any) -> LeftRight[T]:
        if isinstance(other, LeftRight):
            return LeftRight(*(a + b for a, b in zip(self, other, strict=True)))
        if isinstance(other, float | int):
            return LeftRight(*(a + other for a in self))
        return NotImplemented

    def __mul__(self, other: Any) -> LeftRight[T]:
        if isinstance(other, LeftRight):
            return LeftRight(*(a * b for a, b in zip(self, other, strict=True)))
        if isinstance(other, float | int):
            return LeftRight(*(a * other for a in self))
        return NotImplemented

    def normalise(self) -> LeftRight[T]:
        if not isinstance(self.left, float | int):
            return NotImplemented
        total = sum(self)
        return self * (1 / total) if total != 0 else self


class FourCorner[T](NamedTuple):
    """Represents a property with values for each corner of the vehicle.

    Attributes:
        fl (T): Value for the front left corner.
        fr (T): Value for the front right corner.
        rl (T): Value for the rear left corner.
        rr (T): Value for the rear right corner.

    """

    fl: T
    fr: T
    rl: T
    rr: T

    @property
    def front(self) -> LeftRight[T]:
        return LeftRight(self.fl, self.fr)

    @property
    def rear(self) -> LeftRight[T]:
        return LeftRight(self.rl, self.rr)

    @property
    def left(self) -> FrontRear[T]:
        return FrontRear(self.fl, self.rl)

    @property
    def right(self) -> FrontRear[T]:
        return FrontRear(self.fr, self.rr)

    def __add__(self, other: Any) -> FourCorner[T]:
        if isinstance(other, FourCorner):
            return FourCorner(
                *(a + b for a, b in zip(self, other, strict=True)),
            )
        if isinstance(other, float | int):
            return FourCorner(*(a + other for a in self))
        return NotImplemented

    def __mul__(self, other: Any) -> FourCorner[T]:
        if isinstance(other, FourCorner):
            return FourCorner(
                *(a * b for a, b in zip(self, other, strict=True)),
            )
        if isinstance(other, float | int):
            return FourCorner(*(a * other for a in self))
        return NotImplemented
