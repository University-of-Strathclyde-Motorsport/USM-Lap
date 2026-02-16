"""
This package contains modules implementing data channels.
"""

from . import library
from .channel import Channel


def get_channel(channel_name: str) -> type[Channel]:
    """
    Get a data channel from its name.

    Args:
        channel_name (str): The name of the data channel.

    Raises:
        KeyError: If no data channel with the given name exists.

    Returns:
        channel (type[Channel]): A data channel object.
    """
    return Channel.get_channel(channel_name)
