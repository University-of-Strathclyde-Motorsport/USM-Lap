"""Unit tests for the ``usmlap.core.serialisable`` module."""

import json
from pathlib import Path

import pytest

from usmlap.core.serialisable import *


class SerialisableClass(Serialisable):
    prop_1: str
    prop_2: int
    prop_3: NestedSerialisableClass


class NestedSerialisableClass(Serialisable):
    nested_prop_1: float
    nested_prop_2: bool


@pytest.fixture
def serialisable_class() -> SerialisableClass:
    return SerialisableClass(
        prop_1="test",
        prop_2=42,
        prop_3=NestedSerialisableClass(nested_prop_1=3.14, nested_prop_2=True),
    )


@pytest.fixture
def serialisable_class_as_dict() -> dict:
    return {
        "prop_1": "test",
        "prop_2": 42,
        "prop_3": {"nested_prop_1": 3.14, "nested_prop_2": True},
    }


@pytest.fixture
def invalid_data() -> dict:
    return {"prop_1": "test"}


def test_serialisable_as_dict(
    serialisable_class: SerialisableClass, serialisable_class_as_dict: dict
):
    assert serialisable_class.as_dict() == serialisable_class_as_dict


def test_serialisable_io(serialisable_class: SerialisableClass, tmp_path: Path):
    for extension in list_file_formats():
        filepath = (tmp_path / "serialisable").with_suffix(extension)
        serialisable_class.write_file(filepath)
        loaded_class = SerialisableClass.from_file(filepath)
        assert loaded_class == serialisable_class


def test_initialise(serialisable_class: SerialisableClass, tmp_path: Path):
    filepath = tmp_path / "serialisable.json"
    serialisable_class.write_file(filepath)

    assert (
        SerialisableClass.initialise(serialisable_class) == serialisable_class
    )
    assert SerialisableClass.initialise(filepath) == serialisable_class
    assert SerialisableClass.initialise(str(filepath)) == serialisable_class


def test_deserialise_error(invalid_data: dict, tmp_path: Path):
    filepath = tmp_path / "invalid.json"
    with open(filepath, "w") as f:
        f.write(json.dumps(invalid_data))

    with pytest.raises(LibraryLoadError) as exc_info:
        SerialisableClass.from_file(filepath)

    assert str(filepath) in str(exc_info.value)
    assert SerialisableClass.__name__ in str(exc_info.value)


def test_overwrite_file(serialisable_class: SerialisableClass, tmp_path: Path):
    filepath = tmp_path / "serialisable.json"
    with open(filepath, "w") as f:
        f.write("Initial data")

    serialisable_class.write_file(filepath)
    with open(filepath, "r") as f:
        data = f.read()
    assert "Initial data" in data

    serialisable_class.write_file(filepath, overwrite=True)
    with open(filepath, "r") as f:
        data = f.read()
    assert "Initial data" not in data


def test_serialise_error(serialisable_class: SerialisableClass, tmp_path: Path):
    filepath = tmp_path / "serialisable.invalid"
    with pytest.raises(LibraryWriteError) as exc_info:
        serialisable_class.write_file(filepath)

    assert str(filepath) in str(exc_info.value)
    assert SerialisableClass.__name__ in str(exc_info.value)


def test_get_file_format_from_path():
    for extension in list_file_formats():
        format = get_file_format(extension)
        path = Path("test_file").with_suffix(extension)
        assert get_file_format(path) == format


def test_yaml_load_array_raises_error(tmp_path: Path):
    filepath = tmp_path / "array.yaml"
    with open(filepath, "w") as f:
        f.write("- item1\n- item2\n")

    with pytest.raises(ValueError), open(filepath, "r") as f:
        load_yaml_dict(f)
