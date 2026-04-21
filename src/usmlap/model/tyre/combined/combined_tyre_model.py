"""
This module defines the interface for combined tyre models.
"""

from abc import ABC, abstractmethod


class CombinedTyreModel(ABC):
    """Abstract base class for combined tyre models."""

    @abstractmethod
    def available_fy(
        self, fx_max: float, fy_max: float, fx_required: float
    ) -> float: ...

    @abstractmethod
    def available_fx(
        self, fx_max: float, fy_max: float, fy_required: float
    ) -> float: ...
