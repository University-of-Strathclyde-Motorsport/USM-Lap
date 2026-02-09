"""
This module defines the interface for data channels.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from simulation.solution import Solution
from utils.units import Unit

from .functions import ChannelFcn


class Channel(ABC):
    """
    An abstract class representing a data channel.

    A channel can be extracted from a solution by calling
    `channel(solution)`
    where `solution` is a `Solution` object.
    """

    _REGISTRY: dict[str, type[Channel]] = {}
    name: str
    unit: Unit

    def __init_subclass__(
        cls: type[Channel], name: str, unit: Unit = Unit.UNITLESS
    ) -> None:
        super().__init_subclass__()
        cls._REGISTRY[name] = cls
        cls.name = name
        cls.unit = unit

    def __new__(cls, solution: Solution) -> list[float]:
        """
        Overwrite the __new__ method to allow for static calls.

        """
        return cls._channel_fcn()(solution)

    @classmethod
    def get_values(cls, solution: Solution) -> list[float]:
        """
        Extract a list of values from a solution.

        The values are converted to the channel's units.

        Args:
            solution (Solution): A solution object.

        Returns:
            values (list[float]): The values of the corresponding data channel.
        """
        si_values = cls._channel_fcn()(solution)
        return [cls.unit.convert(value) for value in si_values]

    @classmethod
    def get_channel(cls, channel_name: str) -> type[Channel]:
        """
        Get a data channel from its name.

        Args:
            channel_name (str): The name of the data channel.

        Raises:
            KeyError: If no data channel with the given name exists.

        Returns:
            channel (type[Channel]): A data channel object.
        """
        try:
            return cls._REGISTRY[channel_name]
        except KeyError:
            error_message = (
                f"Data channel '{channel_name}' not found. "
                f"Available channels: {list(cls._REGISTRY.keys())}"
            )
            raise KeyError(error_message)

    @classmethod
    def list_channels(cls) -> list[str]:
        """
        Get a list of available data channels.

        Returns:
            channels (list[str]): Available data channel names.
        """
        return list(cls._REGISTRY.keys())

    @classmethod
    def get_label(cls) -> str:
        """
        Get a label for a graph.

        The label is in the format *"{name} ({unit})"*.
        If the unit is None, the label is in the format *"{name} (-)"*.

        Returns:
            label (str): A label with the name and unit of the channel.
        """
        if cls.unit:
            return f"{cls.name} ({cls.unit})"
        else:
            return f"{cls.name} (-)"

    @classmethod
    @abstractmethod
    def _channel_fcn(cls) -> ChannelFcn:
        """
        Function that returns the channel values from a solution.

        Returns:
            channel_fcn (ChannelFcn):
                A function which takes a solution and returns a list of floats.
        """
        ...
