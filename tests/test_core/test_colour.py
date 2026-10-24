"""Unit tests for the `usmlap.core.colour` module."""

import pytest

from usmlap.core.colour import HexColour


def test_valid_colours():
    for colour in ["#003366", "#7abf9E", "#ABCDEF"]:
        HexColour(colour)


def test_invalid_colours():
    for colour in ["003366", "#abcdeg", "#12345", "#1234567"]:
        with pytest.raises(ValueError):
            HexColour(colour)
