"""
This module defines the endurance and efficiency events at Formula Student.
"""

from copy import copy
from math import ceil

from usmlap.track.mesh import Mesh, MeshGenerator
from usmlap.track.track_data import TrackData, load_track_from_spreadsheet
from usmlap.vehicle.parameters import DischargeCurrentLimit, get_new_vehicle
from usmlap.vehicle.vehicle import Vehicle

from .event import EventInterface

ENDURANCE_TRACK_LENGTH = 22000


class Endurance(EventInterface):
    """
    Endurance and efficiency events at Formula Student.
    """

    def load_track(self) -> TrackData:
        track_file = self.competition_settings.autocross_track
        track_data = load_track_from_spreadsheet(track_file)
        # TODO
        return track_data

    def generate_mesh(self) -> Mesh:
        """
        Overwrite mesh generation to repeat the track for the endurance event.
        """
        track_data = self.load_track()
        base_mesh = MeshGenerator(resolution=1).generate_mesh(track_data)
        number_of_laps = ceil(ENDURANCE_TRACK_LENGTH / base_mesh.track_length)
        endurance_mesh = base_mesh.get_repeating_mesh(number_of_laps)
        return endurance_mesh

    def modify_vehicle_for_event(self, vehicle: Vehicle) -> Vehicle:
        return get_new_vehicle(vehicle, DischargeCurrentLimit, 0.3)
