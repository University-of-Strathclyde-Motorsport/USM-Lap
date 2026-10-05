"""
This module implements a generic registry for registering classes.

https://dev.to/dentedlogic/stop-writing-giant-if-else-chains-master-the-python-registry-pattern-ldm
"""

from collections.abc import Iterable


class Registry[KT, VT]:
    """Generic implementation of the registry pattern."""

    def __init__(self) -> None:
        self._store: dict[KT, VT] = {}

    def __contains__(self, key: KT) -> bool:
        return key in self._store

    def list_keys(self) -> Iterable[KT]:
        """Return a list of all keys currently registered.

        Returns:
            list[KT]: A list containing all registered keys.
        """
        return self._store.keys()

    def register(self, key: KT, value: VT) -> None:
        """Register a value in the registry.

        Args:
            key (KT): The unique identifier for the stored value.
            value (VT): The item to store.

        Raises:
            ValueError: If the key is already registered.
        """
        if key in self:
            raise ValueError(f"Key '{key}' is already registered.")
        self._store[key] = value

    def get(self, key: KT) -> VT:
        """Retrieve a value by its key.

        Args:
            key (KT): The unique identifier to look up.

        Returns:
            VT: The stored value associated with the key.

        Raises:
            KeyError: If the key is not found in the registry.
        """
        if key in self:
            return self._store[key]
        raise KeyError(f"Key '{key}' not found in registry.")

    def get_key(self, value: VT) -> KT:
        """Get the first key corresponding to a value in the registry.

        Args:
            value (VT): The value to search for.

        Returns:
            KT: The first key associated with the value.

        Raises:
            KeyError: If the value is not registered in the registry.
        """
        for k, v in self._store.items():
            if v == value:
                return k
        raise KeyError(f"Value '{value}' not registered in registry.")
