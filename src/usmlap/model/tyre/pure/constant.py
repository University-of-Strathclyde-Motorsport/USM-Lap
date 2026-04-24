"""
This module implements a constant tyre model, which assumes that the effective grip coefficient is cosntant.

This tyre model is unsuitable for real simulation, and strictly for testing purposes.
"""

from usmlap.model.tyre import PureTyreModel, TyreAttitude
from usmlap.vehicle import Tyre


class ConstantTyre(PureTyreModel):
    """Constant tyre model."""

    def maximum_fx(self, tyre: Tyre, attitude: TyreAttitude) -> float:
        return tyre.mu_x_peak * attitude.normal_load

    def maximum_fy(self, tyre: Tyre, attitude: TyreAttitude) -> float:
        return tyre.mu_y_peak * attitude.normal_load
