"""
This module contains utility functions for generating vehicles.
"""

from collections.abc import Collection, Iterator
from dataclasses import dataclass

import numpy as np

from usmlap.vehicle import Parameter, Vehicle, get_new_vehicle


def linspace(start: float, end: float, steps: int) -> list[float]:
    """
    Generate a list of `steps` evenly spaced values between `start` and `end`.

    Example:
        >>> linspace(0, 10, 6)
        [0, 2, 4, 6, 8, 10]
    """
    return np.linspace(start, end, steps).tolist()


def geomspace(start: float, end: float, steps: int) -> list[float]:
    """
    Generate a list of `steps` logarithmically spaced values between `start` and `end`.

    Example:
        >>> geomspace(1, 1000, 4)
        [1, 10, 100, 1000]
    """
    return np.geomspace(start, end, steps).tolist()


def step_array(start: float, end: float, step_size: float) -> list[float]:
    """
    Generate a list of values between `start` and `end` with a specified `step_size`.
    The end value may not be included in the list.

    Example:
        >>> step_size(0, 1.5, 2)
        [0, 0.2, 0.4, 0.6, 0.8, 1, 1.2, 1.4]
    """
    return np.arange(start, end, step_size).tolist()


@dataclass
class VehicleGenerator[T](Collection[Vehicle]):
    """Generate a list of vehicles from a set of discrete values."""

    baseline_vehicle: Vehicle
    parameter: type[Parameter[T]]
    values: list[T]

    def __len__(self) -> int:
        return len(self.values)

    def __iter__(self) -> Iterator[Vehicle]:
        for value in self.values:
            yield get_new_vehicle(self.baseline_vehicle, self.parameter, value)

    def __contains__(self, value: Vehicle) -> bool:
        return value in iter(self)
