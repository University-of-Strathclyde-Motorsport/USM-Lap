"""
This module defines exceptions raised by vehicle models.
"""

from dataclasses import dataclass

from usmlap.utils.datatypes import FourCorner


class ModelError(Exception):
    """
    Base class for exceptions raised by vehicle models.
    """


@dataclass
class MaximumIterationsExceededError(ModelError):
    """
    Error raised when the maximum number of iterations is exceeded
    without converging on a solution.
    """

    iterations: int
    precision: float
    residuals: list[float]

    @property
    def _final_error(self) -> float:
        if len(self.residuals) < 2:
            return 0
        return abs(self.residuals[-1] - self.residuals[-2])

    def __str__(self) -> str:
        return (
            f"Failed to converge to desired precision {self.precision} "
            f"after {self.iterations} iterations. "
            f"Final error: {self._final_error}\n"
            f"Residuals: {self.residuals}"
        )


@dataclass
class InsufficientTractionError(ModelError):
    """
    Error raised when the vehicle has insufficient traction.
    """

    required: float
    available: float

    @property
    def ratio(self) -> float:
        return self.required / self.available

    def __str__(self) -> str:
        return (
            f"Insufficient traction "
            f"(required: {self.required:.3f}, "
            f"available: {self.available:.3f})"
        )


@dataclass
class OutOfChargeError(ModelError):
    """
    Error raised when the vehicle is out of battery.
    """

    def __str__(self) -> str:
        return "Vehicle is out of battery."


@dataclass
class WheelLiftError(ModelError):
    """
    Error raised when one or more wheels have negative normal forces.

    This is usually caused by extreme load transfer,
    typically in the first couple of solver iterations.
    """

    loads: FourCorner[float]
    ax: float
    ay: float

    def __str__(self) -> str:
        return "One or more wheels have negative normal loads."

    def __repr__(self) -> str:
        return f"WheelLiftError({self.loads=}, {self.ax=}, {self.ay=})"

    @property
    def lateral_load_transfer(self) -> float:
        left_load = self.loads.front_left + self.loads.rear_left
        right_load = self.loads.front_right + self.loads.rear_right
        return abs(left_load - right_load)

    @property
    def longitudinal_load_transfer(self) -> float:
        front_load = self.loads.front_left + self.loads.front_right
        rear_load = self.loads.rear_left + self.loads.rear_right
        return abs(front_load - rear_load)

    @property
    def max_wheel_lift(self) -> float:
        return abs(min(self.loads))
