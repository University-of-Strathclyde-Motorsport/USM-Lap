"""Unit tests for the `usmlap.core.colour` module."""

import pytest
from pydantic import TypeAdapter, ValidationError

from usmlap.core.colour import HexColour


def test_valid_colours():
    for colour in ["#003366", "#7abf9E", "#ABCDEF"]:
        HexColour(colour)


def test_invalid_colours():
    for colour in ["003366", "#abcdeg", "#12345", "#1234567"]:
        with pytest.raises(ValueError):
            HexColour(colour)


def test_pydantic_coerces_valid_colour_strings():
    colour = TypeAdapter(HexColour).validate_python("#FF6454")

    assert type(colour) is HexColour
    assert colour == "#FF6454"


def test_pydantic_rejects_invalid_colour_strings():
    with pytest.raises(ValidationError):
        TypeAdapter(HexColour).validate_python("#abcdeg")
