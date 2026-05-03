"""
This module defines an interface for telemetry channels.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from textwrap import wrap
from typing import ClassVar, NamedTuple, Optional

from pint.facets.plain import PlainUnit as Unit

from usmlap.solver import SolutionNode
from usmlap.telemetry.data import TelemetrySolution


class TelemetryChannel[T](NamedTuple):
    """
    A telemetry channel.

    Args:
        channel_fcn (Callable[[TelemetrySolution], T]): Extracts a value or series of values from a solution.
        unit (Unit): The physical unit for the channel.
        label (str): A label for the channel.
    """

    channel_fcn: Callable[[TelemetrySolution], T]
    unit: Unit
    label: str

    def __call__(self, solution: TelemetrySolution) -> T:
        # TODO: unit conversion
        print("Calling telemetry channel")
        print(self.channel_fcn)
        return self.channel_fcn(solution)

    def label_with_unit(self, wrap_width: Optional[int] = 25) -> str:
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
        label = f"{self.label} ({self.unit:~P})"

        if wrap_width is not None:
            lines = wrap(label, width=wrap_width)
            label = "\n".join([line.center(wrap_width) for line in lines])

        return label


type ScalarChannel = TelemetryChannel[float]
type DataChannel = TelemetryChannel[list[float]]


class PrimitiveDataChannel(ABC):
    """
    Base class for primitive telemetry data channels.

    These channels extract a list of values from a telemetry solution.
    Each value corresponds to a node in the solution.
    """

    unit: ClassVar[Unit]
    label: ClassVar[str]

    @classmethod
    def __init_subclass__(cls, *, unit: Unit, label: str) -> None:
        super().__init_subclass__()
        cls.unit = unit
        cls.label = label

    @classmethod
    @abstractmethod
    def read_value(cls, node: SolutionNode) -> float: ...

    def __new__(
        cls, unit: Optional[Unit] = None, label: Optional[str] = None
    ) -> TelemetryChannel[list[float]]:
        def channel_fcn(solution: TelemetrySolution) -> list[float]:  # noqa: S1720
            return [cls.read_value(node) for node in solution.nodes]

        if not unit:
            unit = cls.unit

        if not label:
            label = cls.label

        return TelemetryChannel(channel_fcn, unit, label)


class DerivedDataChannel(ABC):
    """
    Base class for derived telemetry data channels.
    """

    unit: ClassVar[Unit]
    label: ClassVar[str]

    @classmethod
    def __init_subclass__(cls, *, unit: Unit, label: str) -> None:
        super().__init_subclass__()
        cls.unit = unit
        cls.label = label

    @classmethod
    @abstractmethod
    def channel_fcn(cls, solution: TelemetrySolution) -> list[float]: ...

    def __new__(
        cls, unit: Optional[Unit] = None, label: Optional[str] = None
    ) -> TelemetryChannel[list[float]]:

        if not unit:
            unit = cls.unit

        if not label:
            label = cls.label

        return TelemetryChannel(cls.channel_fcn, unit, label)
