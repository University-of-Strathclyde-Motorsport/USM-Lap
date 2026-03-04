"""
This module defines the endurance and efficiency events at Formula Student.
"""

from usmlap.track.track_data import TrackData, load_track_from_spreadsheet

from .event import EventInterface


class Endurance(EventInterface):
    """
    Endurance and efficiency events at Formula Student.
    """

    def load_track(self) -> TrackData:
        track_file = self.competition_settings.autocross_track
        track_data = load_track_from_spreadsheet(track_file)
        # TODO
        return track_data
