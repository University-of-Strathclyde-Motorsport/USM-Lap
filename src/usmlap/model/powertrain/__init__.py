"""
This subpackage contains definitions of powertrain models.
"""

from usmlap.core.registry import Registry
from usmlap.model.powertrain.interface import PowertrainModelInterface
from usmlap.model.powertrain.single_motor_rwd import SingleMotorRWD

PowertrainModelRegistry = Registry[str, type[PowertrainModelInterface]]()
PowertrainModelRegistry.register("single-motor-rwd", SingleMotorRWD)
