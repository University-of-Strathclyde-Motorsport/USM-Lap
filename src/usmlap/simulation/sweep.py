"""
This module implements code for sweeping through values.
"""

from collections.abc import Generator, Iterable
from dataclasses import dataclass, field
from itertools import groupby
from typing import Any


@dataclass
class IncompatibleSweepDimensionError(Exception):
    """Raised if a sweep has incompatible dimensions."""

    arrays: dict[int, list[tuple[str, ...]]]

    def __str__(self) -> str:
        def _format_arrays(arrays: Iterable[tuple[str, ...]]) -> str:
            """Format a list of nested keys."""
            return ", ".join(f"'{format_nested_key(arr)}'" for arr in arrays)

        arrays = [
            f"{n}: {_format_arrays(arrs)}" for n, arrs in self.arrays.items()
        ]
        return (
            f"All arrays in a sweep must be the same length.\n"
            f"{'\n'.join(arrays)}"
        )


@dataclass
class SweepDefinition:
    """Definitions of parameters to be swept."""

    arrays: dict[tuple[str, ...], list[Any]]
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

    def _build_dictionary(self, i: int) -> dict[str, Any]:
        d: dict[str, Any] = {}
        for nested_key, v in self.arrays.items():
            cursor = d
            for k in nested_key[:-1]:
                cursor = cursor.setdefault(k, {})
            cursor[nested_key[-1]] = v[i]
        return d

    def __iter__(self) -> Generator[dict[str, Any]]:
        for i in range(len(self)):
            yield self._build_dictionary(i)


def generate_sweep_definition(definition: dict[str, Any]) -> SweepDefinition:
    """Generate a sweep definition from a dictionary."""
    arrays = _get_arrays(definition)
    return SweepDefinition(arrays=arrays)


def _get_arrays(
    d: dict[str, Any], _location: tuple[str, ...] = ()
) -> dict[tuple[str, ...], list[Any]]:
    """Get a dict of arrays and their locations from a nested dictionary."""
    arrays: dict[tuple[str, ...], list[Any]] = {}
    for k, v in d.items():
        key_location = (*_location, k)
        if isinstance(v, dict):
            arrays.update(_get_arrays(v, _location=key_location))
        else:
            arrays[key_location] = v
    return arrays


def merge_dicts(
    base: dict[str, Any], new: dict[str, Any], *, allow_new_keys: bool = True
) -> dict[str, Any]:
    """Update a dictionary with values from another."""
    for k, v in new.items():
        if k not in base:
            if allow_new_keys:
                base[k] = v
            else:
                raise ValueError(f"Cannot add key '{k}' to dictionary")
        elif isinstance(v, dict):
            base[k] = merge_dicts(base[k], v, allow_new_keys=allow_new_keys)
        else:
            base[k] = v
    return base


def format_nested_key(key: tuple[str, ...]) -> str:
    """Format a nested dictionary key with dots between parts."""
    return ".".join(key)
