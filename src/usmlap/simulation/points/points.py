"""
This module contains code for calculating points from competition results.
"""

from dataclasses import dataclass
from .points_functions import PointsFunctions, FSUKPointsFunctions
from .competition_data import CompetitionData
from ..competition import CompetitionResults
import matplotlib.pyplot as plt


@dataclass
class CompetitionPoints(object):
    """
    Points scored in each event at Formula Student.

    Attributes:
        acceleration (float): Points scored in the acceleration event.
        skidpad (float): Points scored in the skidpad event.
        autocross (float): Points scored in the autocross event.
        endurance (float): Points scored in the endurance event.
    """

    acceleration: float
    skidpad: float
    autocross: float
    endurance: float

    @property
    def total(self) -> float:
        return (
            self.acceleration + self.skidpad + self.autocross + self.endurance
        )

    def plot_pie_chart(self) -> None:
        """
        Plot a pie chart of points scored in each event.
        """
        points = {
            "Acceleration": self.acceleration,
            "Skidpad": self.skidpad,
            "Autocross": self.autocross,
            "Endurance": self.endurance,
        }
        plt.pie(list(points.values()), labels=list(points.keys()))
        plt.show()


def calculate_points(
    results: CompetitionResults,
    data: CompetitionData = CompetitionData(),
    formulae: PointsFunctions = FSUKPointsFunctions(),
) -> CompetitionPoints:
    """
    Calculate points scored in each event at Formula Student.

    Args:
        results (CompetitionResults):
            The results of a competition simulation.
        data (Optional[CompetitionData]):
            The competition data to use for calculating points.
        formulae (PointsFunctions, optional):
            The points formulae to use.

    Returns:
        points (CompetitionPoints): The points scored in each event.
    """
    points = CompetitionPoints(
        acceleration=formulae.calculate_acceleration_points(
            t_team=results.acceleration.total_time,
            t_min=data.acceleration_t_min,
        ),
        skidpad=formulae.calculate_skidpad_points(
            t_team=results.skidpad.total_time / 2,
            t_min=data.skidpad_t_min,
        ),
        autocross=formulae.calculate_autocross_points(
            t_team=results.autocross.total_time,
            t_min=data.autocross_t_min,
        ),
        endurance=formulae.calculate_endurance_points(
            t_team=results.endurance.total_time,
            t_min=data.endurance_t_min,
        ),
    )
    return points
