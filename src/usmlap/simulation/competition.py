"""
This module contains code for simulating a complete Formula Student competition.
"""

from __future__ import annotations
from dataclasses import dataclass
from vehicle.vehicle import Vehicle
from track.mesh import MeshGenerator
from track.track_data import TrackData
from .solution import Solution
from .simulation import Simulation


LIBRARY_ROOT = "D:/Repositories/USM-Lap/appdata/library/"
ACCELERATION_TRACK = LIBRARY_ROOT + "tracks/Acceleration.xlsx"
SKIDPAD_TRACK = LIBRARY_ROOT + "tracks/Skidpad.xlsx"


@dataclass
class Competition(object):
    """
    A simulation of a complete Formula Student competition.

    Simulates all four events:
    acceleration, skidpad, autocross, and endurance.


    Attributes:
        vehicle (Vehicle): The vehicle to simulate.
        track (Mesh): The track to use for autocross and endurance.
        environment (Environment): Environmental variables for the simulation.
        vehicle_model_type (VehicleModelInterface): The vehicle model to use.
        solver_type (SolverInterface): The solver to use.
    """

    vehicle: Vehicle
    autocross_track: str

    def simulate(self) -> CompetitionResults:
        return CompetitionResults(
            acceleration=self.simulate_acceleration(),
            skidpad=self.simulate_skidpad(),
            autocross=self.simulate_autocross(),
            endurance=self.simulate_endurance(),
        )

    def simulate_acceleration(self) -> Solution:
        track_data = TrackData.load_track_from_spreadsheet(ACCELERATION_TRACK)
        mesh = MeshGenerator(resolution=1).generate_mesh(track_data)
        simulation = Simulation(vehicle=self.vehicle, track=mesh)
        return simulation.simulate()

    def simulate_skidpad(self) -> Solution:
        track_data = TrackData.load_track_from_spreadsheet(SKIDPAD_TRACK)
        mesh = MeshGenerator(resolution=1).generate_mesh(track_data)
        simulation = Simulation(vehicle=self.vehicle, track=mesh)
        return simulation.simulate()

    def simulate_autocross(self) -> Solution:
        track_data = TrackData.load_track_from_spreadsheet(self.autocross_track)
        mesh = MeshGenerator(resolution=1).generate_mesh(track_data)
        simulation = Simulation(vehicle=self.vehicle, track=mesh)
        return simulation.simulate()

    def simulate_endurance(self) -> Solution:
        track_data = TrackData.load_track_from_spreadsheet(self.autocross_track)
        mesh = (
            MeshGenerator(resolution=1)
            .generate_mesh(track_data)
            .generate_endurance_mesh()
        )
        simulation = Simulation(vehicle=self.vehicle, track=mesh)
        return simulation.simulate()


@dataclass
class CompetitionResults(object):
    """
    The results of a competition simulation

    Attributes:
        acceleration (Solution): The solution to the acceleration event.
        skidpad (Solution): The solution to the skidpad event.
        autocross (Solution): The solution to the autocross event.
        endurance (Solution): The solution to the endurance event.
    """

    acceleration: Solution
    skidpad: Solution
    autocross: Solution
    endurance: Solution
