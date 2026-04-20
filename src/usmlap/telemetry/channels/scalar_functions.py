"""
This module defines scalar functions which can operate on telemetry channels.
"""

from usmlap.telemetry.data import TelemetrySolution

from .channel import DataChannel, ScalarChannel, ScalarValue


def total(channel: DataChannel) -> ScalarChannel:
    """Add up the values of a channel."""

    def inner(solution: TelemetrySolution) -> ScalarValue:
        return sum(channel(solution))

    return inner


def maximum(channel: DataChannel) -> ScalarChannel:
    """Find the maximum value of a channel."""

    def inner(solution: TelemetrySolution) -> ScalarValue:
        return max(channel(solution))

    return inner


def minimum(channel: DataChannel) -> ScalarChannel:
    """Find the minimum value of a channel."""

    def inner(solution: TelemetrySolution) -> ScalarValue:
        return min(channel(solution))

    return inner


def initial(channel: DataChannel) -> ScalarChannel:
    """Get the value at the first index of a channel."""

    def inner(solution: TelemetrySolution) -> ScalarValue:
        return channel(solution)[0]

    return inner


def final(channel: DataChannel) -> ScalarChannel:
    """Get the value at the last index of a channel."""

    def inner(solution: TelemetrySolution) -> ScalarValue:
        return channel(solution)[-1]

    return inner


def delta(channel: DataChannel) -> ScalarChannel:
    """Get the difference between the initial and final values of a channel."""

    def inner(solution: TelemetrySolution) -> ScalarValue:
        return final(channel)(solution) - initial(channel)(solution)

    return inner
