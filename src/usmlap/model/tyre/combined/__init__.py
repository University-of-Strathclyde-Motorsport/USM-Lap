"""
This subpackage defines combined tyre models.
"""

from usmlap.core.registry import Registry
from usmlap.model.tyre.combined.friction_ellipse import FrictionEllipse
from usmlap.model.tyre.tyre_model import CombinedTyreModel

CombinedTyreModelRegistry = Registry[str, type[CombinedTyreModel]]()
CombinedTyreModelRegistry.register("friction-ellipse", FrictionEllipse)
