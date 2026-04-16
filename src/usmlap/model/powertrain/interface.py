"""
This module defines a common interface for powertrain models.
"""

from abc import ABC, abstractmethod

from ..context import NodeContext


class PowertrainModelInterface(ABC):
    """
    Abstract base class for powertrain models.
    """

    @abstractmethod
    def required_torque(
        self, ctx: NodeContext, drive_force: float
    ) -> float: ...

    @abstractmethod
    def required_current(self, ctx: NodeContext, torque: float) -> float: ...

    @abstractmethod
    def motor_torque(self, ctx: NodeContext, velocity: float) -> float: ...

    @abstractmethod
    def drive_force(self, ctx: NodeContext, velocity: float) -> float: ...
