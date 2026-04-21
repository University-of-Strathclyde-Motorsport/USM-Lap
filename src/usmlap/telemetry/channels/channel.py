"""
This module defines an interface for telemetry channels.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import NamedTuple, Protocol, Self

from usmlap.solver import SolutionNode
from usmlap.telemetry.data import TelemetrySolution
from usmlap.utils.units import Unit

type TelemetryChannel[T] = Callable[[TelemetrySolution], T]

type ScalarValue = float
type ScalarChannel = TelemetryChannel[ScalarValue]
type ScalarFunction = Callable[[DataChannel], ScalarChannel]

type DataChannelValues = list[float]
type DataChannel = TelemetryChannel[DataChannelValues]


class ChannelFunctionProtocol(Protocol):
    """Protocol for channel functions."""

    label: str
    unit: Unit

    def __call__(self, *channels: DataChannel) -> DataChannel: ...


class DataChannelBase(ABC):
    """
    Base class for telemetry data channels.

    A data channel extracts a list of values from a telemetry solution.
    """

    def __call__(self, solution: TelemetrySolution) -> DataChannelValues:
        return self.read_values(solution)

    def __init_subclass__(cls, label: str, unit: Unit) -> None:
        super().__init_subclass__()
        cls.label = label
        cls.unit = unit

    def read_values(self, solution: TelemetrySolution) -> DataChannelValues:
        return [self.get_value(node) for node in solution.nodes]

    @abstractmethod
    def get_value(self, node: SolutionNode) -> float: ...


class TelemetryChannelProductType[T](NamedTuple):
    """Attempty 2."""

    function: Callable[[TelemetrySolution], T]
    label: str
    unit: Unit

    def __add__(self, other) -> Self:
        if isinstance(other, TelemetryChannelProductType):
            
