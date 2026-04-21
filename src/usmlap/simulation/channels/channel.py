"""
This module defines the interface for data channels.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from textwrap import wrap
from typing import Optional

from usmlap.solver import Solution
from usmlap.utils.units import Unit


@dataclass
class IncompatibleUnitError(ValueError):
    """Raised when a channel cannot be converted to a given unit."""

    # TODO: move this to unit module
    unit: Unit
    channel: Channel

    def __str__(self) -> str:
        return (
            f"Unit '{self.unit}' of quantity '{self.unit.quantity}' does not match "
            f"the quantity '{self.channel.unit.quantity}' for channel '{self.channel.name}'."
        )


# class ChannelBase[T](ABC):
#     pass
#     # @abstractmethod
#     # def unit_conversion(value: T, unit: Unit) -> T: ...


# type ChannelCallable[T: ChannelSize] = Callable[[Solution], T]
# class ChannelReturnType[T](ABC):
#     def __init__(self, value: T) -> None:
#         self.value = value

#     @abstractmethod
#     def unit_conversion(self, unit: Unit) -> T: ...


# class DataChannel(ChannelReturnType[list[float]]):
#     def __init__(self, value: list[float]) -> None:
#         super().__init__(value)

#     def unit_conversion(self, unit: Unit) -> list[float]:
#         return [unit.convert(v) for v in self.value]

type Data = list[float]
type Lap = list[float]
type Scalar = float

type ChannelType = Data | Lap | Scalar


# class LapChannel(ChannelReturnType[list[float]]):
#     def unit_conversion(self, unit: Unit) -> list[float]:
#         return [unit.convert(v) for v in self.value]


# class ScalarChannel(ChannelReturnType[float]):
#     def unit_conversion(self, unit: Unit) -> float:
#         return unit.convert(self.value)


class Channel[T: ChannelType](ABC):
    """
    An abstract class representing a data channel.

    Channels must define the _channel_fcn class method,
    which returns a ChannelFcn callable.
    This callable accepts a Solution object,
    and returns a list of floats corresponding to the values of the channel.

    Attributes:
        name (str): The name of the channel,
            used to access it from the channel registry.
        unit (Unit): The default unit to use when displaying the channel.
    """

    name: str
    unit: Unit

    def __init_subclass__(
        cls: type[Channel], name: str, unit: Unit = Unit.UNITLESS
    ) -> None:
        super().__init_subclass__()
        cls.name = name
        cls.unit = unit

    def __call__(
        self,
        solution: Solution,
        *,
        unit: Optional[Unit] = None,
        indices: Optional[list[int]] = None,
    ) -> T:
        if indices is not None:
            solution = solution.get_subset(indices)

        si_values = self._channel_fcn(solution)
        return si_values

    def get_values(self, solution: Solution, unit: Optional[Unit] = None) -> T:
        if unit is None:
            unit = self.unit
        else:
            if unit.quantity != self.unit.quantity:
                raise IncompatibleUnitError(unit, self)

        si_values = self.__call__(solution)
        return [unit.convert(value) for value in si_values]

    @abstractmethod
    def _channel_fcn(self, solution: Solution) -> T:
        """
        Function that returns the channel values from a solution.

        Returns:
            channel_fcn (ChannelFcn):
                A function which takes a solution and returns a list of floats.
        """
        ...

    @classmethod
    def get_label(cls, wrap_width: Optional[int] = 25) -> str:
        """
        Get a label for a graph.
        Long labels will be formatted into multiple lines.

        The label is in the format *"{name} ({unit})"*.
        If the unit is None, the label is in the format *"{name}"*.

        Args:
            wrap_width (Optional[int]): The width to wrap the label to.
                To disable wrapping, set to None.

        Returns:
            label (str): A label with the name and unit of the channel.
        """
        # TODO: move this to unit module
        if cls.unit:
            label = f"{cls.name} ({cls.unit})"
        else:
            label = f"{cls.name}"

        if wrap_width is not None:
            lines = wrap(label, width=wrap_width)
            label = "\n".join([line.center(wrap_width) for line in lines])

        return label


# class DataChannel(ChannelBase[list[float]]):
#     pass
#     # def unit_conversion(value: list[float], unit: Unit) -> list[float]:
#     #     return [unit.convert(v) for v in value]


# class LapChannel(ChannelBase[list[float]]):
#     pass


# def unit_conversion(value: list[float], unit: Unit) -> list[float]:
#     return [unit.convert(v) for v in value]


# class ScalarChannel(ChannelSize[float]):
#     pass
# def unit_conversion(value: float, unit: Unit) -> float:
#     return unit.convert(value)
