"""
This module defines channel functions which operate on each element of a telemetry channel.
"""

import math
from itertools import accumulate

from usmlap.telemetry.data import TelemetrySolution

from .channel import DataChannel, DataChannelValues


def negate(channel: DataChannel) -> DataChannel:
    """Negate the values of a data channel."""

    def inner(solution: TelemetrySolution) -> DataChannelValues:
        values = channel(solution)
        return [-v for v in values]

    return inner


def add(channel_1: DataChannel, channel_2: DataChannel) -> DataChannel:
    """Add the values of `channel_1` and `channel_2`."""

    def inner(solution: TelemetrySolution) -> DataChannelValues:
        values_1 = channel_1(solution)
        values_2 = channel_2(solution)
        return [v1 + v2 for v1, v2 in zip(values_1, values_2)]

    return inner


def subtract(channel_1: DataChannel, channel_2: DataChannel) -> DataChannel:
    """Subtract the values of `channel_2` from `channel_1`."""

    def inner(solution: TelemetrySolution) -> DataChannelValues:
        values_1 = channel_1(solution)
        values_2 = channel_2(solution)
        return [v1 - v2 for v1, v2 in zip(values_1, values_2)]

    return add(channel_1, negate(channel_2))


def product(channel_1: DataChannel, channel_2: DataChannel) -> DataChannel:
    """Calculate the element-wise product of two channels."""

    def inner(solution: TelemetrySolution) -> DataChannelValues:
        values_1 = channel_1(solution)
        values_2 = channel_2(solution)
        return [v1 * v2 for v1, v2 in zip(values_1, values_2)]

    return inner


def divide(channel_1: DataChannel, channel_2: DataChannel) -> DataChannel:
    """Perform element-wise division of two channels."""

    def inner(solution: TelemetrySolution) -> DataChannelValues:
        values_1 = channel_1(solution)
        values_2 = channel_2(solution)
        return [v1 / v2 for v1, v2 in zip(values_1, values_2)]

    return inner


def power(channel: DataChannel, exponent: float) -> DataChannel:
    """Raise the values of a channel to a power."""

    def inner(solution: TelemetrySolution) -> DataChannelValues:
        values = channel(solution)
        return [v**exponent for v in values]

    return inner


def square(channel: DataChannel) -> DataChannel:
    """Square the values of a channel."""
    return power(channel, 2)


def square_root(channel: DataChannel) -> DataChannel:
    """Calculate the square root of the values of a channel."""

    def inner(solution: TelemetrySolution) -> DataChannelValues:
        values = channel(solution)
        return [math.sqrt(v) for v in values]

    return inner


def hypotenuse(channel_1: DataChannel, channel_2: DataChannel) -> DataChannel:
    """
    Compute the hypotenuse of a right-angled triangle,
    with side lengths given by the values of `channel_1` and `channel_2`.
    """
    return square_root(add(square(channel_1), square(channel_2)))


def cumulative_sum(channel: DataChannel) -> DataChannel:
    """Calculate the cumulative sum of a channel."""

    def inner(solution: TelemetrySolution) -> DataChannelValues:
        values = channel(solution)
        return list(accumulate(values))

    return inner


def difference(channel: DataChannel) -> DataChannel:
    """
    Compute the different between consecutive values of a channel.

    In order to preserve the length of the channel,
    each value is the average of the forward and backward differences.
    """

    def inner(solution: TelemetrySolution) -> DataChannelValues:
        values = channel(solution)
        values.insert(0, 0)
        values.append(0)
        difference = [
            0.5 * (right - left) for left, right in zip(values[:-1], values[1:])
        ]
        return difference[1:-1]

    return inner


def derivative(channel: DataChannel, wrt: DataChannel) -> DataChannel:
    """Compute the derivative of one channel with respect to another."""
    return divide(difference(channel), wrt)


def intergral(channel: DataChannel, wrt: DataChannel) -> DataChannel:
    """Compute the integral of one channel with respect to another."""
    return cumulative_sum(product(channel, wrt))


def absolute(channel: DataChannel) -> DataChannel:
    """Get the absolute value of every element of a channel."""

    def inner(solution: TelemetrySolution) -> DataChannelValues:
        values = channel(solution)
        return [abs(v) for v in values]

    return inner
