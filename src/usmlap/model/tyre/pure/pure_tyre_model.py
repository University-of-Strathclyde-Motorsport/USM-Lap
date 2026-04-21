"""
This module defines the interface for pure tyre models.
"""

from abc import ABC, abstractmethod

from usmlap.model.tyre.tyre_model import TyreAttitude
from usmlap.vehicle import Tyre


class PureTyreModel(ABC):
    """Abstract base class for pure tyre models."""

    @abstractmethod
    def maximum_fx(self, tyre: Tyre, attitude: TyreAttitude) -> float: ...

    @abstractmethod
    def maximum_fy(self, tyre: Tyre, attitude: TyreAttitude) -> float: ...
