"""
This module defines a common interface for powertrain models.
"""

from abc import ABC, abstractmethod

from ..context import Context


class PowertrainModelInterface(ABC):
    """
    Abstract base class for powertrain models.
    """

    @abstractmethod
    def drive_force(self, ctx: Context, velocity: float) -> float: ...
