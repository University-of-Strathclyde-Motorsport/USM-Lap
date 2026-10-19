"""Unit tests for the `usmlap.core.nested_dict` module."""

import pytest

from usmlap.core.nested_dict import (
    format_keypath,
    get_nested_value,
    merge_dicts,
    parse_keypath,
    set_nested_value,
)


def test_merge_dicts():
    old = {"abc": [1, 2, 3], "def": {"ghi": [4, 5, 6], "jkl": [7, 8, 9]}}
    new = {"abc": [2, 3, 4], "new": 10, "def": {"xyz": 0, "jkl": 100}}
    expected = {
        "abc": [2, 3, 4],
        "new": 10,
        "def": {"ghi": [4, 5, 6], "jkl": 100, "xyz": 0},
    }
    assert merge_dicts(old, new) == expected


def test_merge_dict_new_key_is_forbidden():
    old = {"abc": 123}
    new = {"new": 456}
    with pytest.raises(ValueError):
        merge_dicts(old, new, allow_new_keys=False)


def test_format_keypath():
    assert format_keypath(("abc", "def", "ghi")) == "abc.def.ghi"


def test_format_keypath_alternative_delimiter():
    assert format_keypath(("abc", "def", "ghi"), "|") == "abc|def|ghi"


def test_format_keypath_invalid_delimiter():
    with pytest.raises(ValueError):
        format_keypath(("abc.", "def."))


def test_parse_keypath():
    assert parse_keypath("abc.def.ghi") == ("abc", "def", "ghi")


def test_parse_keypath_scalar():
    assert parse_keypath("abc") == ("abc",)


def test_parse_keypath_alternative_delimiter():
    assert parse_keypath("abc|def|ghi", "|") == ("abc", "def", "ghi")


def test_get_nested_value():
    assert get_nested_value({"abc": {"def": 1}}, ("abc", "def"), int) == 1


def test_get_nested_value_simple():
    assert get_nested_value({"abc": 1}, ("abc",), int) == 1


def test_get_nested_value_coerce():
    assert isinstance(get_nested_value({"abc": 1}, ("abc",), str), str)


def test_get_nested_value_empty_path_raises_error():
    with pytest.raises(KeyError):
        get_nested_value({}, (), int)


def test_get_nested_value_intermediate_value_raises_error():
    with pytest.raises(TypeError):
        get_nested_value({"abc": "not_a_dict"}, ("abc", "def"), int)


def test_get_nested_value_missing_value_raises_error():
    with pytest.raises(KeyError):
        get_nested_value({"abc": 1}, ("def",), int)


def test_get_nested_value_coercion_error():
    with pytest.raises(TypeError):
        get_nested_value({"abc": "NaN"}, ("abc",), int)
    with pytest.raises(TypeError):
        get_nested_value({"abc": {"def": 1}}, ("abc",), int)


def test_set_nested_value():
    assert set_nested_value({}, ("abc", "def"), 1) == {"abc": {"def": 1}}


def test_set_nested_value_preserves_existing_keys():
    assert set_nested_value({"abc": 1}, ("def",), 2) == {"abc": 1, "def": 2}


def test_set_nested_value_empty_path_raises_error():
    with pytest.raises(KeyError):
        set_nested_value({}, (), 1)
