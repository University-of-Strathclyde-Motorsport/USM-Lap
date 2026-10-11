"""Unit tests for the `usmlap.core.registry` module."""

import pytest

from usmlap.core.registry import Registry


def test_registering_and_retrieving():
    registry = Registry[str, int]()
    registry.register("abc", 1)
    assert registry.get("abc") == 1


def test_registering_duplicate_key_raises_error():
    registry = Registry[str, int]()
    registry.register("abc", 1)
    with pytest.raises(ValueError):
        registry.register("abc", 2)


def test_getting_missing_key_raises_error():
    registry = Registry[str, int]()
    with pytest.raises(KeyError):
        registry.get("abc")


def test_get_key_by_value():
    registry = Registry[str, int]()
    registry.register("abc", 1)
    assert registry.get_key(1) == "abc"


def test_get_key_for_missing_value_raises_error():
    registry = Registry[str, int]()
    with pytest.raises(KeyError):
        registry.get_key(1)


def test_contains_method():
    registry = Registry[str, int]()
    registry.register("abc", 1)
    assert "abc" in registry


def test_list_keys():
    registry = Registry[str, int]()
    registry.register("abc", 1)
    registry.register("def", 2)
    assert list(registry.list_keys()) == ["abc", "def"]
