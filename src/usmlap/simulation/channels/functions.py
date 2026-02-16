"""
This module defines functions for working with data channels.
"""

import math
from collections.abc import Callable
from itertools import accumulate

from simulation.solution import Solution

type ChannelFcn = Callable[[Solution], list[float]]


def negate(channel: ChannelFcn) -> ChannelFcn:
    """
    Perform element-wise negation of a channel.

    Args:
        channel (ChannelFcn): A channel.

    Returns:
        negation (ChannelFcn):
            A function that returns the negation of the channel.
    """

    def inner(solution: Solution) -> list[float]:
        """Inner function."""
        values = channel(solution)
        return [-v for v in values]

    return inner


def add(channel_1: ChannelFcn, channel_2: ChannelFcn) -> ChannelFcn:
    """
    Add the values of two channels.

    Args:
        channel_1 (ChannelFcn): A channel.
        channel_2 (ChannelFcn): Another channel.

    Returns:
        sum (ChannelFcn): The sum of the channels.
    """

    def inner(solution: Solution) -> list[float]:
        """Inner function."""
        values_1 = channel_1(solution)
        values_2 = channel_2(solution)
        return [a + b for a, b in zip(values_1, values_2)]

    return inner


def subtract(channel_1: ChannelFcn, channel_2: ChannelFcn) -> ChannelFcn:
    """
    Subtract the value of `channel_2` from `channel_1`.

    Args:
        channel_1 (ChannelFcn): A channel to subtract from.
        channel_2 (ChannelFcn): Another channel to be subtracted.

    Returns:
        result (ChannelFcn): The difference between the channels.
    """
    return add(channel_1, negate(channel_2))


def product(channel_1: ChannelFcn, channel_2: ChannelFcn) -> ChannelFcn:
    """
    Perform element-wise multiplication of two channels.

    Args:
        channel_1 (ChannelFcn): A channel.
        channel_2 (ChannelFcn): Another channel.

    Returns:
        product (ChannelFcn):
            A function that returns the product of the channels.
    """

    def inner(solution: Solution) -> list[float]:
        """Inner function."""
        values_1 = channel_1(solution)
        values_2 = channel_2(solution)
        return [v1 * v2 for v1, v2 in zip(values_1, values_2)]

    return inner


def divide(channel_1: ChannelFcn, channel_2: ChannelFcn) -> ChannelFcn:
    """
    Perform element-wise division of two channels.

    Args:
        channel_1 (ChannelFcn): A channel to be divided.
        channel_2 (ChannelFcn): Another channel to divide by.

    Returns:
        division (ChannelFcn):
            A function that returns the division of the channels.
    """

    def inner(solution: Solution) -> list[float]:
        """Inner function."""
        values_1 = channel_1(solution)
        values_2 = channel_2(solution)
        return [v1 / v2 for v1, v2 in zip(values_1, values_2)]

    return inner


def power(channel: ChannelFcn, exponent: float) -> ChannelFcn:
    """
    Raise the values of a channel to a power.

    Args:
        channel (ChannelFcn): A channel.
        exponent (float): The exponent to raise the channel to.

    Returns:
        results (ChannelFcn): The channel raised to the exponent.
    """

    def inner(solution: Solution) -> list[float]:
        """Inner function."""
        values = channel(solution)
        return [v**exponent for v in values]

    return inner


def square(channel: ChannelFcn) -> ChannelFcn:
    """
    Square the values of a channel.

    Args:
        channel (ChannelFcn): A channel.

    Returns:
        results (ChannelFcn): The channel squared.
    """
    return power(channel, 2)


def square_root(channel: ChannelFcn) -> ChannelFcn:
    """
    Calculate the square root of the values of a channel.

    Args:
        channel (ChannelFcn): A channel.

    Returns:
        square_root (ChannelFcn): The square root of the channel.
    """

    def inner(solution: Solution) -> list[float]:
        """Inner function."""
        values = channel(solution)
        return [math.sqrt(v) for v in values]

    return inner


def hypotenuse(channel_1: ChannelFcn, channel_2: ChannelFcn) -> ChannelFcn:
    """
    Compute the hypotenuse of a right triangle.

    Args:
        channel_1 (ChannelFcn): A channel.
        channel_2 (ChannelFcn): Another channel.

    Returns:
        hypotenuse (ChannelFcn):
            A function that returns the length of the hypotenuse
            of a triange formed by the two channels.
    """

    return square_root(add(square(channel_1), square(channel_2)))


def difference(channel: ChannelFcn) -> ChannelFcn:
    """
    Compute the difference between consecutive values of a channel.

    Each value is the average of the forward and backward differences.
    The first and last values are the true differences.
    This preserves the length of the channel.

    Args:
        channel (ChannelFcn): A channel to take the difference of.

    Returns:
        difference (ChannelFcn): The differences of the channel.
    """

    def inner(solution: Solution) -> list[float]:
        """Inner function."""
        x = channel(solution)
        true_diff = [x[i + 1] - x[i] for i in range(len(x) - 1)]
        average_diff = [
            0.5 * (true_diff[i + 1] + true_diff[i])
            for i in range(len(true_diff) - 1)
        ]
        return [true_diff[0], *average_diff, true_diff[-1]]

    return inner


def cumulative_sum(channel: ChannelFcn) -> ChannelFcn:
    """
    Calculate the cumulative sum of a channel.

    Args:
        channel (ChannelFcn): A channel.

    Returns:
        cumulative_sum (ChannelFcn):
            A function that returns the cumulative sum of the channel.
    """

    def inner(solution: Solution) -> list[float]:
        """Inner function."""
        values = channel(solution)
        return list(accumulate(values))

    return inner


def derivative(channel: ChannelFcn, wrt: ChannelFcn) -> ChannelFcn:
    """
    Calculate the time derivative of a channel.

    Args:
        channel (ChannelFcn): A channel to differentiate.
        wrt (ChannelFcn): The channel with differentiate with respect to.

    Returns:
        time_derivative (ChannelFcn):
            A function that returns the derivative of the channel.
    """

    return divide(difference(channel), wrt)


def integral(channel: ChannelFcn, wrt: ChannelFcn) -> ChannelFcn:
    """
    Calculate the integral of a channel.

    Args:
        channel (ChannelFcn): A channel to integrate.
        wrt (ChannelFcn): The channel to integrate with respect to.

    Returns:
        integral (ChannelFcn):
            A function that returns the integral of the channel.
    """

    return cumulative_sum(product(channel, wrt))
