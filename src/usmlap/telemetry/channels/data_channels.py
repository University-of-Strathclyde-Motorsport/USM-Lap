"""
This module defines data channels for telemetry data.
"""

from usmlap.telemetry.data import TelemetrySolution

from .channel import DataChannelBase, DataChannelValues


class Velocity(DataChannelBase):
    """Velocity of the vehicle."""

    def read_values(self, solution: TelemetrySolution) -> DataChannelValues:
        return [node.average_velocity for node in solution.nodes]


class Position(DataChannelBase):
    """Position of the vehicle."""

    def read_values(self, solution: TelemetrySolution) -> DataChannelValues:
        return [node.track_node.position for node in solution.nodes]


class NodeTime(DataChannelBase):
    """Time taken to traverse the track node."""

    def read_values(self, solution: TelemetrySolution) -> DataChannelValues:
        return [node.time for node in solution.nodes]
