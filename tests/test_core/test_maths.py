"""Unit tests for the `usmlap.core.maths` module."""

import math

import numpy as np
import pytest

from usmlap.core.maths import area_of_circle, clamp, interp_previous


def test_clamp():
    assert clamp(-1.5, minimum=0) == 0
    assert clamp(7, maximum=5.9) == 5.9
    assert clamp(0.5, minimum=0, maximum=1) == 0.5
    assert clamp(0, minimum=0, maximum=0) == 0
    with pytest.raises(ValueError):
        clamp(0, minimum=1, maximum=-1)


def test_area_of_circle():
    assert area_of_circle(0) == 0
    assert area_of_circle(2) == math.pi
    assert area_of_circle(4) == 4 * math.pi
    with pytest.raises(ValueError):
        area_of_circle(-1)


def test_interp_previous():
    assert np.all(
        interp_previous(
            np.array([0.7, 2.5, -1]),
            np.array([0, 1, 2]),
            np.array(["a", "b", "c"]),
        )
        == ["a", "c", "a"]
    )

    assert np.all(
        interp_previous(
            np.array([3]),
            np.array([0, 1, 2]),
            np.array(["a", "b", "c"]),
        )
        == ["c"]
    )

    assert np.all(
        interp_previous(
            np.array([-1]),
            np.array([0, 1, 2]),
            np.array(["a", "b", "c"]),
        )
        == ["a"]
    )

    assert np.all(
        interp_previous(
            np.array([-1]),
            np.array([0, 1, 2]),
            np.array(["a", "b", "c"]),
        )
        == ["a"]
    )

    with pytest.raises(ValueError):
        interp_previous(np.array([]), np.array([0, 1, 2]), np.array(["a", "b"]))
    with pytest.raises(ValueError):
        interp_previous(np.array([]), np.array([]), np.array([]))
    with pytest.raises(ValueError):
        interp_previous(
            np.array([]), np.array([2, 1, 3]), np.array(["a", "b", "c"])
        )
    with pytest.raises(ValueError):
        interp_previous(
            np.array([]), np.array([1, 1, 3]), np.array(["a", "b", "c"])
        )
