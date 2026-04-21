"""
This module defines the interface for tyre models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import NamedTuple

from usmlap.model.tyre.combined import CombinedTyreModel
from usmlap.model.tyre.pure import PureTyreModel
from usmlap.vehicle import Tyre


class TyreAttitude(NamedTuple):
    """Variables describing the state of a tyre."""

    normal_load: float
    slip_angle: float = 0
    slip_ratio: float = 0
    camber: float = 0


@dataclass
class TyreModel(object):
    """Tyre model object."""

    longitudinal: PureTyreModel
    lateral: PureTyreModel
    combined: CombinedTyreModel

    @abstractmethod
    def available_fx(
        self, tyre: Tyre, tyre_attitude: TyreAttitude, required_fy: float = 0
    ) -> float: ...

    @abstractmethod
    def available_fy(
        self, tyre: Tyre, tyre_attitude: TyreAttitude, required_fx: float = 0
    ) -> float: ...
