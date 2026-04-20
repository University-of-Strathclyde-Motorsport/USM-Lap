"""
This module defines exceptions raised by vehicle models.
"""

from dataclasses import dataclass


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
