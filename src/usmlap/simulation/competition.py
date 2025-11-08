"""
This module contains code for simulating a complete Formula Student competition.
"""

from __future__ import annotations
from dataclasses import dataclass
from copy import deepcopy
import logging
import filepath
from vehicle.vehicle import Vehicle
from track.mesh import MeshGenerator
from track.track_data import TrackData
from .solution import Solution
from .simulation import SimulationSettings, simulate

ACCELERATION_TRACK = filepath.LIBRARY_ROOT / "tracks" / "Acceleration.xlsx"
SKIDPAD_TRACK = filepath.LIBRARY_ROOT / "tracks" / "Skidpad.xlsx"


def simulate_competition(
    vehicle: Vehicle, settings: SimulationSettings
) -> CompetitionResults:
    """
    Simulates all four Formula Student events:
    acceleration, skidpad, autocross, and endurance.

    Args:
        vehicle (Vehicle): The vehicle to simulate.
        settings (SimulationSettings): Settings for the simulation.

    Returns:
        results (CompetitionResults): The results of all four simulations.
    """
    return CompetitionResults(
        acceleration=simulate_acceleration(vehicle, settings),
        skidpad=simulate_skidpad(vehicle, settings),
        autocross=simulate_autocross(vehicle, settings),
        endurance=simulate_endurance(vehicle, settings),
    )


def simulate_acceleration(
    vehicle: Vehicle, settings: SimulationSettings
) -> Solution:
    """
    Simulate the acceleration event.

    Args:
        vehicle (Vehicle): The vehicle to simulate.
        settings (SimulationSettings): Settings for the simulation.

    Returns:
        solution (Solution): The results of the simulation.
    """
    logging.info("Simulating acceleration event...")
    track_data = TrackData.load_track_from_spreadsheet(ACCELERATION_TRACK)
    mesh = MeshGenerator(resolution=1).generate_mesh(track_data)
    acceleration_settings = deepcopy(settings)
    acceleration_settings.track = mesh
    solution = simulate(vehicle=vehicle, settings=acceleration_settings)
    return solution


def simulate_skidpad(
    vehicle: Vehicle, settings: SimulationSettings
) -> Solution:
    """
    Simulate the skidpad event.

    Args:
        vehicle (Vehicle): The vehicle to simulate.
        settings (SimulationSettings): Settings for the simulation.

    Returns:
        solution (Solution): The results of the simulation.
    """
    logging.info("Simulating skidpad event...")
    track_data = TrackData.load_track_from_spreadsheet(SKIDPAD_TRACK)
    mesh = MeshGenerator(resolution=1).generate_mesh(track_data)
    skidpad_settings = deepcopy(settings)
    skidpad_settings.track = mesh
    solution = simulate(vehicle=vehicle, settings=skidpad_settings)
    return solution


def simulate_autocross(
    vehicle: Vehicle, settings: SimulationSettings
) -> Solution:
    """
    Simulate the autocross event.

    Args:
        vehicle (Vehicle): The vehicle to simulate.
        settings (SimulationSettings): Settings for the simulation.

    Returns:
        solution (Solution): The results of the simulation.
    """
    logging.info("Simulating autocross event...")
    solution = simulate(vehicle=vehicle, settings=settings)
    return solution


def simulate_endurance(
    vehicle: Vehicle, settings: SimulationSettings
) -> Solution:
    """
    Simulate the endurance event.

    Args:
        vehicle (Vehicle): The vehicle to simulate.
        settings (SimulationSettings): Settings for the simulation.

    Returns:
        solution (Solution): The results of the simulation.
    """
    logging.info("Simulating endurance event...")
    mesh = settings.track.generate_endurance_mesh()
    endurance_settings = deepcopy(settings)
    endurance_settings.track = mesh
    solution = simulate(vehicle=vehicle, settings=endurance_settings)
    return solution


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
