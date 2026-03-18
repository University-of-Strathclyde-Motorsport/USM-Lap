"""
This module defines the autocross event at Formula Student.
"""

from usmlap.simulation.solution import Solution
from usmlap.track.track_data import TrackData, load_track_from_spreadsheet

from ..points import AUTOCROSS_COEFFICIENTS, CompetitionData, calculate_points
from .event import EventInterface


class Autocross(EventInterface, label="autocross"):
    """
    Autocross event at Formula Student.
    """

    def __init__(self, track_file: str) -> None:
        super().__init__(track_file)

    def load_track(self, track_file: str) -> TrackData:
        track_data = load_track_from_spreadsheet(track_file)
        return track_data

    def calculate_points(
        self, solution: Solution, competition_data: CompetitionData
    ) -> dict[str, float]:

        t_team = solution.total_time
        t_min = competition_data.autocross_t_min
        label, points = calculate_points(t_team, t_min, AUTOCROSS_COEFFICIENTS)
        return {label: points}
