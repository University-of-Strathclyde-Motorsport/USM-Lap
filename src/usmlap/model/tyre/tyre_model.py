"""
This module defines the interface for tyre models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import NamedTuple

from usmlap.vehicle import Tyre


class TyreAttitude(NamedTuple):
    """Variables describing the state of a tyre."""

    normal_load: float
    slip_angle: float = 0
    slip_ratio: float = 0
    camber: float = 0


class PureTyreModel(ABC):
    """Abstract base class for pure tyre models."""

    @abstractmethod
    def maximum_fx(self, tyre: Tyre, attitude: TyreAttitude) -> float: ...

    @abstractmethod
    def maximum_fy(self, tyre: Tyre, attitude: TyreAttitude) -> float: ...


class CombinedTyreModel(ABC):
    """Abstract base class for combined tyre models."""

    @abstractmethod
    def fx(self, fy: float, fx_max: float, fy_max: float) -> float: ...

    @abstractmethod
    def fy(self, fx: float, fx_max: float, fy_max: float) -> float: ...


@dataclass
class TyreModel(object):
    """Tyre model object."""

    longitudinal: PureTyreModel
    lateral: PureTyreModel
    combined: CombinedTyreModel

    def fx_max(self, tyre: Tyre, attitude: TyreAttitude) -> float:
        return self.longitudinal.maximum_fx(tyre, attitude)

    def fy_max(self, tyre: Tyre, attitude: TyreAttitude) -> float:
        return self.lateral.maximum_fy(tyre, attitude)

    def fx(self, fy: float, fx_max: float, fy_max: float) -> float:
        return self.combined.fx(fy, fx_max, fy_max)

    def fy(self, fx: float, fx_max: float, fy_max: float) -> float:
        return self.combined.fy(fx, fx_max, fy_max)
