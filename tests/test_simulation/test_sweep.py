"""Unit tests for the study module."""

from copy import deepcopy

import pytest

from usmlap.simulation.sweep import (
    IncompatibleSweepDimensionError,
    _get_arrays,
    generate_sweep_definition,
    merge_dicts,
)

INPUT = {
    "abc": [1, 2, 3],
    "def": {
        "ghi": [4, 5, 6],
        "jkl": [7, 8, 9],
    },
}

OUTPUT = [
    {
        "abc": 1,
        "def": {
            "ghi": 4,
            "jkl": 7,
        },
    },
    {
        "abc": 2,
        "def": {
            "ghi": 5,
            "jkl": 8,
        },
    },
    {
        "abc": 3,
        "def": {
            "ghi": 6,
            "jkl": 9,
        },
    },
]


def test_get_arrays():
    output = {
        ("abc",): [1, 2, 3],
        ("def", "ghi"): [4, 5, 6],
        ("def", "jkl"): [7, 8, 9],
    }
    assert _get_arrays(INPUT) == output


def test_sweep_definition_length():
    sweep = generate_sweep_definition(INPUT)
    assert len(sweep) == 3


def test_sweep_definition_sweeps():
    sweep = generate_sweep_definition(INPUT)
    assert list(sweep) == OUTPUT


def test_empty_sweep_definition_raises_error():
    with pytest.raises(ValueError):
        generate_sweep_definition({})


def test_incompatible_sweep_dimension_raises_error():
    with pytest.raises(IncompatibleSweepDimensionError):
        generate_sweep_definition({"abc": [1, 2, 3], "de": [1, 2]})


def test_merge_dict():
    new = {"abc": [2, 3, 4], "new": 10, "def": {"xyz": 0, "jkl": 100}}
    expected = {
        "abc": [2, 3, 4],
        "new": 10,
        "def": {"ghi": [4, 5, 6], "jkl": 100, "xyz": 0},
    }
    assert merge_dicts(deepcopy(INPUT), new) == expected


def test_merge_dict_new_key_is_forbidden():
    old = {"abc": 123}
    new = {"new": 456}
    with pytest.raises(ValueError):
        merge_dicts(old, new, allow_new_keys=False)
