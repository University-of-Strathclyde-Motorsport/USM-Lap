def split(total: float, proportions: tuple[float, ...]):
    """
    Split a value proportionally

    Args:
        total (float): Total value
        proportions (tuple[float, ...]): List of proportions

    Returns:
        split_value (tuple[float, ...]): Total split proportionally according to proportions
    """
    return tuple(p * total / sum(proportions) for p in proportions)


def with_complement(proportion: float) -> tuple[float, float]:
    """
    Get a tuple containing a proportion and its complement

    Args:
        proportion (float): Value between 0 and 1

    Returns:
        proportion_with_complement (tuple[float, float]): Tuple of proportion and (1 - proportion)
    """
    complement = 1 - proportion
    return proportion, complement
