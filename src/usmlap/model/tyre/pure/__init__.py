"""
This subpackage defines pure tyre models.
"""

from usmlap.core.registry import Registry
from usmlap.model.tyre.pure.constant import ConstantTyre
from usmlap.model.tyre.pure.linear import LinearTyre
from usmlap.model.tyre.tyre_model import PureTyreModel

PureTyreModelRegistry = Registry[str, type[PureTyreModel]]()
PureTyreModelRegistry.register("constant", ConstantTyre)
PureTyreModelRegistry.register("linear", LinearTyre)
