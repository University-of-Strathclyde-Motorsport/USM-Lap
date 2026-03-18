"""
This module defines the acceleration event at Formula Student.
"""

from usmlap.simulation.solution import Solution

from ..points import (
    ACCELERATION_COEFFICIENTS,
    CompetitionData,
    calculate_points,
)
from .event import EventInterface

ACCELERATION_TRACK = "Acceleration.xlsx"


class Acceleration(EventInterface, label="acceleration"):
    """
    Acceleration event at Formula Student.
    """

    def __init__(self) -> None:
        super().__init__(ACCELERATION_TRACK)

    def calculate_points(
        self, solution: Solution, competition_data: CompetitionData
    ) -> dict[str, float]:

        t_team = solution.total_time
        t_min = competition_data.acceleration_t_min
        label, points = calculate_points(
            t_team, t_min, ACCELERATION_COEFFICIENTS
        )
        return {label: points}
