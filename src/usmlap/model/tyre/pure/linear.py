"""
This module implements a linear, load-sensitive tyre model.
"""

from usmlap.model.tyre.tyre_model import TyreAttitude
from usmlap.vehicle import Tyre

from .pure_tyre_model import PureTyreModel as PureTyreModel


class LinearTyre(PureTyreModel):
    """Linear, load sensitive tyre model."""

    def maximum_fx(self, tyre: Tyre, attitude: TyreAttitude) -> float:
        mu_x = tyre.mu_x_peak - (tyre.mu_x_sens * attitude.normal_load)
        return mu_x * attitude.normal_load

    def maximum_fy(self, tyre: Tyre, attitude: TyreAttitude) -> float:
        mu_y = tyre.mu_y_peak - (tyre.mu_y_sens * attitude.normal_load)
        return mu_y * attitude.normal_load
