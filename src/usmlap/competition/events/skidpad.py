"""
This module defines the skidpad event at Formula Student.
"""

from usmlap.simulation.solution import Solution

from ..points import SKIDPAD_COEFFICIENTS, CompetitionData, calculate_points
from .event import EventInterface

SKIDPAD_TRACK = "Skidpad.xlsx"


class Skidpad(EventInterface, label="skidpad"):
    """
    Skidpad event at Formula Student.
    """

    def __init__(self) -> None:
        super().__init__(SKIDPAD_TRACK)

    def calculate_points(
        self, solution: Solution, competition_data: CompetitionData
    ) -> dict[str, float]:

        t_team = solution.total_time / 2
        t_min = competition_data.skidpad_t_min
        label, points = calculate_points(t_team, t_min, SKIDPAD_COEFFICIENTS)
        return {label: points}
