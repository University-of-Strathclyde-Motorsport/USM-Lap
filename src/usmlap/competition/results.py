"""
This module defines the results of a competition simulation.
"""

from dataclasses import dataclass

from usmlap.simulation.solution import Solution


@dataclass
class CompetitionResults(object):
    """
    The results of a competition simulation.

    Attributes:
        acceleration (Solution): The solution to the acceleration event.
        skidpad (Solution): The solution to the skidpad event.
        autocross (Solution): The solution to the autocross event.
        endurance (Solution): The solution to the endurance event.
    """

    acceleration: Solution
    skidpad: Solution
    autocross: Solution
    endurance: Solution
