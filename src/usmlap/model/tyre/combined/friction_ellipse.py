"""
This module implements the friction ellipse combined tyre model.
"""

import math

from usmlap.model.errors import InsufficientTractionError
from usmlap.model.tyre.tyre_model import CombinedTyreModel


class FrictionEllipse(CombinedTyreModel):
    """Friction ellipse for modelling combined tyre behaviour."""

    def fx(self, fy: float, fx_max: float, fy_max: float) -> float:
        return fx_max * _get_scale_factor(fy, fy_max)

    def fy(self, fx: float, fx_max: float, fy_max: float) -> float:
        return fy_max * _get_scale_factor(fx, fx_max)


def _get_scale_factor(required: float, maximum: float) -> float:
    """Calculate a scale factor for available grip."""
    if required > maximum:
        raise InsufficientTractionError(required, maximum)
    if maximum == 0:
        return 0
    return math.sqrt(1 - (required / maximum) ** 2)
