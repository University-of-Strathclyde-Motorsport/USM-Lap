"""
This module defines settings for simulating a Formula Student competition.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CompetitionSettings(object):
    """
    Settings for simulating a Formula Student competition.
    """

    autocross_track: str
