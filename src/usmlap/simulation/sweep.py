"""
This module implements code for sweeping through values.
"""

from collections.abc import Generator, Iterable
from dataclasses import dataclass, field
from itertools import groupby
from typing import Any

from usmlap.core.nested_dict import KeyPath, NestedDict, set_nested_value


@dataclass
class IncompatibleSweepDimensionError(Exception):
    """Raised if a sweep has incompatible dimensions."""

    keypaths: dict[int, list[KeyPath]]

    def __str__(self) -> str:
        def _format_paths(keypaths: Iterable[KeyPath]) -> str:
            """Format a list of nested keys."""
            return ", ".join(f"'{'.'.join(arr)}'" for arr in keypaths)

        keypaths_by_length = [
            f"{n}: {_format_paths(arrs)}" for n, arrs in self.keypaths.items()
        ]
        return (
            f"All values in a sweep must be the same length.\n"
            f"{'\n'.join(keypaths_by_length)}"
        )


@dataclass
class SweepDefinition:
    """Definitions of parameters to be swept."""

    arrays: dict[KeyPath, list[object]]
    _length: int = field(init=False)

    def __len__(self) -> int:
        return self._length

    def __post_init__(self) -> None:
        groups = groupby(self.arrays, key=lambda x: len(self.arrays[x]))
        arrays_by_length = {n: list(arrays) for n, arrays in groups}
        if len(arrays_by_length) > 1:
            raise IncompatibleSweepDimensionError(arrays_by_length)
        elif len(arrays_by_length) == 0:
            raise ValueError("Sweep must have at least one dimension")
        else:
            self._length = next(iter(arrays_by_length.keys()))

    def _build_dictionary(self, i: int) -> NestedDict:
        d: NestedDict = {}
        for keypath, values in self.arrays.items():
            set_nested_value(d, keypath, values[i])
        return d

    def __iter__(self) -> Generator[NestedDict]:
        for i in range(len(self)):
            yield self._build_dictionary(i)


def generate_sweep_definition(definition: dict[str, Any]) -> SweepDefinition:
    """Generate a sweep definition from a dictionary."""
    arrays = _get_arrays(definition)
    return SweepDefinition(arrays=arrays)


def _get_arrays(
    d: dict[str, Any], _location: KeyPath = ()
) -> dict[KeyPath, list[object]]:
    """Get a dict of arrays and their locations from a nested dictionary."""
    arrays: dict[KeyPath, list[object]] = {}
    for k, v in d.items():
        key_location = (*_location, k)
        if isinstance(v, dict):
            arrays.update(_get_arrays(v, _location=key_location))
        else:
            arrays[key_location] = v
    return arrays
