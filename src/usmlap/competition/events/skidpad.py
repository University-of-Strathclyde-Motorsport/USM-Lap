"""
This module defines the skidpad event at Formula Student.
"""

from usmlap.track.track_data import TrackData, load_track_from_spreadsheet

from .event import EventInterface

SKIDPAD_TRACK = "Skidpad.xlsx"


class Skidpad(EventInterface, label="skidpad"):
    """
    Skidpad event at Formula Student.
    """

    def load_track(self) -> TrackData:
        track_data = load_track_from_spreadsheet(SKIDPAD_TRACK)
        return track_data
