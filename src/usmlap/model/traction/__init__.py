"""
This subpackage contains defintions of traction models.
"""

from usmlap.core.registry import Registry
from usmlap.model.traction.bicycle import Bicycle
from usmlap.model.traction.four_corner import FourCornerModel
from usmlap.model.traction.point_mass import PointMass
from usmlap.model.traction.traction_model import TractionModel

TractionModelRegistry = Registry[str, type[TractionModel]]()
TractionModelRegistry.register("point-mass", PointMass)
TractionModelRegistry.register("bicycle", Bicycle)
TractionModelRegistry.register("four-corner", FourCornerModel)
