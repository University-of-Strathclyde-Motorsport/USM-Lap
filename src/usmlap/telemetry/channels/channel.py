"""
This module defines an interface for telemetry channels.
"""

from abc import ABC, abstractmethod
from typing import Callable

from usmlap.telemetry.data import TelemetrySolution

type TelemetryChannel[T] = Callable[[TelemetrySolution], T]

type ScalarValue = float
type ScalarChannel = TelemetryChannel[ScalarValue]
type ScalarFunction = Callable[[DataChannel], ScalarChannel]

type DataChannelValues = list[float]
type DataChannel = TelemetryChannel[DataChannelValues]
type ChannelFunction = Callable[[DataChannel, ...], DataChannel]


class DataChannelBase(ABC):
    """
    Base class for telemetry data channels.

    A data channel extracts a list of values from a telemetry solution.
    """

    def __call__(self, solution: TelemetrySolution) -> DataChannelValues:
        return self.read_values(solution)

    @abstractmethod
    def read_values(self, solution: TelemetrySolution) -> DataChannelValues: ...
