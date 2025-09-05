"""
This module contains utility functions for working with proportions.
"""


def split(total: float, proportions: tuple[float, ...]):
    """
    Split a value proportionally

    Args:
        total (float): Total value
        proportions (tuple[float, ...]): List of proportions

    Returns:
        split_value (tuple[float, ...]):
            Total split proportionally according to proportions
    """
    return tuple(p * total / sum(proportions) for p in proportions)


def with_complement(proportion: float) -> tuple[float, float]:
    """
    Get a tuple containing a proportion and its complement

    Args:
        proportion (float): Value between 0 and 1

    Returns:
        proportion_with_complement (tuple[float, float]):
            Tuple of proportion and (1 - proportion)
    """
    complement = 1 - proportion
    return proportion, complement


def normalise(values: tuple[float, ...]):
    """
    Normalise a tuple of values.

    Values retain their relative proportions, but sum to 1.

    Args:
        values (tuple[float, float]): Tuple of values

    Returns:
        normalised_values (tuple[float, float]): Tuple of normalised values
    """
    total = sum(values)
    return tuple(v / total for v in values)
