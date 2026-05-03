"""
This module defines channel functions which operate on each element of a telemetry channel.
"""

import math
from itertools import accumulate
from typing import Optional

from pint.facets.plain import PlainUnit as Unit

from usmlap.telemetry import TelemetrySolution

from .channel import DataChannel, TelemetryChannel


def negate(
    channel: DataChannel,
    *,
    unit: Optional[Unit] = None,
    label: Optional[str] = None,
) -> DataChannel:
    """Negate the values of a data channel."""

    def channel_fcn(solution: TelemetrySolution) -> list[float]:  # noqa: S1720
        return [-v for v in channel(solution)]

    if unit is None:
        unit = channel.unit

    if label is None:
        label = f"-{channel.label}"

    return TelemetryChannel(channel_fcn, unit=unit, label=label)


def add(channel_1: DataChannel, channel_2: DataChannel) -> DataChannel:
    """Add the values of `channel_1` and `channel_2`."""

    def channel_fcn(solution: TelemetrySolution) -> list[float]:  # noqa: S1720
        data_1 = channel_1(solution)
        data_2 = channel_2(solution)
        return [v1 + v2 for v1, v2 in zip(data_1, data_2)]

    # Check units
    unit = channel_1.unit
    label = f"{channel_1.label} + {channel_2.label}"

    return TelemetryChannel(channel_fcn, unit, label)


def subtract(channel_1: DataChannel, channel_2: DataChannel) -> DataChannel:
    """Subtract the values of `channel_2` from `channel_1`."""

    return add(channel_1, negate(channel_2))


def product(channel_1: DataChannel, channel_2: DataChannel) -> DataChannel:
    """Calculate the element-wise product of two channels."""

    def channel_fcn(solution: TelemetrySolution) -> list[float]:  # noqa: S1720
        values_1 = channel_1(solution)
        values_2 = channel_2(solution)
        return [v1 * v2 for v1, v2 in zip(values_1, values_2)]

    unit = channel_1.unit * channel_2.unit
    label = f"{channel_1.label} * {channel_2.label}"

    return TelemetryChannel(channel_fcn, unit, label)


def divide(channel_1: DataChannel, channel_2: DataChannel) -> DataChannel:
    """Perform element-wise division of two channels."""

    def channel_fcn(solution: TelemetrySolution) -> list[float]:  # noqa: S1720
        data_1 = channel_1(solution)
        data_2 = channel_2(solution)
        return [v1 / v2 for v1, v2 in zip(data_1, data_2)]

    unit = channel_1.unit / channel_2.unit
    label = f"{channel_1.label} / {channel_2.label}"

    return TelemetryChannel(channel_fcn, unit, label)


def power(channel: DataChannel, exponent: float) -> DataChannel:
    """Raise the values of a channel to a power."""

    def channel_fcn(solution: TelemetrySolution) -> list[float]:  # noqa: S1720
        values = channel(solution)
        return [v**exponent for v in values]

    label = f"{channel.label}^{exponent}"
    unit = (channel.unit) ** exponent

    return TelemetryChannel[list[float]](channel_fcn, unit, label)


def square(channel: DataChannel) -> DataChannel:
    """Square the values of a channel."""
    return power(channel, 2)


def square_root(channel: DataChannel) -> DataChannel:
    """Calculate the square root of the values of a channel."""

    def channel_fcn(solution: TelemetrySolution) -> list[float]:  # noqa: S1720
        values = channel(solution)
        return [math.sqrt(v) for v in values]

    unit = channel.unit**0.5
    label = f"sqrt({channel.label})"

    return TelemetryChannel(channel_fcn, unit, label)


def hypotenuse(channel_1: DataChannel, channel_2: DataChannel) -> DataChannel:
    """
    Compute the hypotenuse of a right-angled triangle,
    with side lengths given by the values of `channel_1` and `channel_2`.
    """
    return square_root(add(square(channel_1), square(channel_2)))


def cumulative_sum(channel: DataChannel) -> DataChannel:
    """Calculate the cumulative sum of a channel."""

    def channel_fcn(solution: TelemetrySolution) -> list[float]:  # noqa: S1720
        values = channel(solution)
        return list(accumulate(values))

    unit = channel.unit
    label = f"Cumulative {channel.label}"

    return TelemetryChannel(channel_fcn, unit, label)


def difference(channel: DataChannel) -> DataChannel:
    """
    Compute the different between consecutive values of a channel.

    In order to preserve the length of the channel,
    each value is the average of the forward and backward differences.
    """

    def channel_fcn(solution: TelemetrySolution) -> list[float]:  # noqa: S1720
        values = channel(solution)
        values.insert(0, 0)
        values.append(0)
        difference = [
            0.5 * (right - left) for left, right in zip(values[:-1], values[1:])
        ]
        return difference

    label = f"Delta {channel.label}"
    return TelemetryChannel(channel_fcn, channel.unit, label)


def derivative(channel: DataChannel, wrt: DataChannel) -> DataChannel:
    """Compute the derivative of one channel with respect to another."""
    return divide(difference(channel), wrt)


def integral(channel: DataChannel, wrt: DataChannel) -> DataChannel:
    """Compute the integral of one channel with respect to another."""
    return cumulative_sum(product(channel, wrt))


def absolute(channel: DataChannel) -> DataChannel:
    """Get the absolute value of every element of a channel."""

    def channel_fcn(solution: TelemetrySolution) -> list[float]:  # noqa: S1720
        values = channel(solution)
        return [abs(v) for v in values]

    unit = channel.unit
    label = f"|{channel.label}|"

    return TelemetryChannel(channel_fcn, unit, label)
