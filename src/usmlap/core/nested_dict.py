"""
This module defines functions for working with nested dictionaries.
"""

from typing import Any

type NestedDict = dict[str, Any]
type KeyPath = tuple[str, ...]


def format_keypath(keypath: KeyPath, delimiter: str = ".") -> str:
    """Format a nested dictionary key with dots between parts."""
    for key in keypath:
        if delimiter in key:
            raise ValueError(
                f"Cannot format keypath with delimiter '{delimiter}'; ",
                "delimiter must not be present in any key",
            )
    return delimiter.join(keypath)


def merge_dicts(
    base: NestedDict, new: NestedDict, *, allow_new_keys: bool = True
) -> NestedDict:
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


def set_nested_value(
    nested_dict: NestedDict, keypath: KeyPath, value: object
) -> NestedDict:
    """Set a value in a nested dictionary."""
    if len(keypath) == 0:
        raise KeyError("Keypath cannot be empty")
    cursor = nested_dict
    for k in keypath[:-1]:
        cursor = cursor.setdefault(k, {})
    cursor[keypath[-1]] = value
    return nested_dict
