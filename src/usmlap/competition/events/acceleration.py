"""
This module defines the acceleration event at Formula Student.
"""

from usmlap.track.track_data import TrackData, load_track_from_spreadsheet

from .event import EventInterface

ACCELERATION_TRACK = "Acceleration.xlsx"


class Acceleration(EventInterface, label="acceleration"):
    """
    Acceleration event at Formula Student.
    """

    def load_track(self) -> TrackData:
        track_data = load_track_from_spreadsheet(ACCELERATION_TRACK)
        return track_data
