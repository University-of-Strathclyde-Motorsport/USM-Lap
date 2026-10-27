"""Unit tests for the `usmlap.core.colour` module."""

import pytest
from pydantic import TypeAdapter, ValidationError

from usmlap.core.colour import N_COLOUR_MAX, HexColour, get_n_colours


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


def test_get_n_colours():
    for n in range(1, N_COLOUR_MAX + 1):
        colours = get_n_colours(n)
        assert len(colours) == n


def test_get_n_colours_invalid_n():
    with pytest.raises(ValueError):
        get_n_colours(0)
    with pytest.raises(ValueError):
        get_n_colours(N_COLOUR_MAX + 1)
