"""
This module contains code for calculating points from competition results.
"""

from dataclasses import dataclass
from .points_functions import PointsFunctions, FSUKPointsFunctions
from .competition_data import CompetitionData
from ..competition import CompetitionResults
import matplotlib.pyplot as plt


@dataclass
class PointsCalculator(object):
    """
    A points calculator for the Formula Student UK competition.
    """

    competition_results: CompetitionResults
    competition_data: CompetitionData = CompetitionData()
    points_formulae: PointsFunctions = FSUKPointsFunctions()

    @property
    def acceleration_points(self) -> float:
        t_team = self.competition_results.acceleration.total_time
        t_min = self.competition_data.acceleration_t_min
        return self.points_formulae.calculate_acceleration_points(t_team, t_min)

    @property
    def skidpad_points(self) -> float:
        t_team = self.competition_results.skidpad.total_time / 2
        t_min = self.competition_data.skidpad_t_min
        return self.points_formulae.calculate_skidpad_points(t_team, t_min)

    @property
    def autocross_points(self) -> float:
        t_team = self.competition_results.autocross.total_time
        t_min = self.competition_data.autocross_t_min
        return self.points_formulae.calculate_autocross_points(t_team, t_min)

    @property
    def endurance_points(self) -> float:
        t_team = self.competition_results.endurance.total_time
        t_min = self.competition_data.endurance_t_min
        return self.points_formulae.calculate_endurance_points(t_team, t_min)

    @property
    def total_points(self) -> float:
        return (
            self.acceleration_points
            + self.skidpad_points
            + self.autocross_points
            + self.endurance_points
        )

    def plot_pie_chart(self) -> None:
        points = [
            self.acceleration_points,
            self.skidpad_points,
            self.autocross_points,
            self.endurance_points,
        ]
        labels = [
            "Acceleration",
            "Skidpad",
            "Autocross",
            "Endurance",
        ]
        plt.pie(points, labels=labels)
        plt.show()
