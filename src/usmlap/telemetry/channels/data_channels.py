"""
This module defines data channels for telemetry data.
"""

from usmlap.solver import SolutionNode
from usmlap.telemetry.data import TelemetrySolution
from usmlap.utils.units import Unit

from .channel import ChannelFunctionProtocol, DataChannelBase


class Velocity(DataChannelBase, label="Velocity", unit=Unit.METER_PER_SECOND):
    """Velocity of the vehicle."""

    def get_value(self, node: SolutionNode) -> float:
        return node.average_velocity


class Position(DataChannelBase, label="Position", unit=Unit.METER):
    """Position of the vehicle."""

    def get_value(self, node: SolutionNode) -> float:
        return node.track_node.position


class NodeTime(DataChannelBase, label="Node Time", unit=Unit.METER):
    """Time taken to traverse the track node."""

    def get_value(self, node: SolutionNode) -> float:
        return node.time


x: list[ChannelFunctionProtocol] = []