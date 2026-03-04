"""
This module defines the autocross event at Formula Student.
"""

from usmlap.track.track_data import TrackData, load_track_from_spreadsheet

from .event import EventInterface


class Autocross(EventInterface):
    """
    Autocross event at Formula Student.
    """

    def load_track(self) -> TrackData:
        track_file = self.competition_settings.autocross_track
        track_data = load_track_from_spreadsheet(track_file)
        return track_data
