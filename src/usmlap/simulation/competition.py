"""
This module contains code for simulating a complete Formula Student competition.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from usmlap.track.mesh import MeshGenerator
from usmlap.track.track_data import TrackData, load_track_from_spreadsheet
from usmlap.vehicle.vehicle import Vehicle

from .simulation import SimulationSettings, simulate
from .solution import Solution

ACCELERATION_TRACK = "Acceleration.xlsx"
SKIDPAD_TRACK = "Skidpad.xlsx"


@dataclass
class CompetitionSettings(object):
    """
    Settings for a complete competition simulation.

    Attributes:
        autocross_track (TrackData): The track to use for the autocross event.
        simulation_settings (SimulationSettings): Settings for each simulation.
    """

    autocross_track: TrackData
    simulation_settings: SimulationSettings


def simulate_competition(
    vehicle: Vehicle, settings: CompetitionSettings
) -> CompetitionResults:
    """
    Simulates all four Formula Student events:
    acceleration, skidpad, autocross, and endurance.

    Args:
        vehicle (Vehicle): The vehicle to simulate.
        settings (CompetitionSettings): Settings for the simulation.

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
    vehicle: Vehicle, settings: CompetitionSettings
) -> Solution:
    """
    Simulate the acceleration event.

    Args:
        vehicle (Vehicle): The vehicle to simulate.
        settings (CompetitionSettings): Settings for the simulation.

    Returns:
        solution (Solution): The results of the simulation.
    """
    logging.info("Simulating acceleration event...")
    track_data = load_track_from_spreadsheet(ACCELERATION_TRACK)
    mesh = MeshGenerator(resolution=1).generate_mesh(track_data)
    solution = simulate(
        vehicle=vehicle, track_mesh=mesh, settings=settings.simulation_settings
    )
    return solution


def simulate_skidpad(
    vehicle: Vehicle, settings: CompetitionSettings
) -> Solution:
    """
    Simulate the skidpad event.

    Args:
        vehicle (Vehicle): The vehicle to simulate.
        settings (CompetitionSettings): Settings for the simulation.

    Returns:
        solution (Solution): The results of the simulation.
    """
    logging.info("Simulating skidpad event...")
    track_data = load_track_from_spreadsheet(SKIDPAD_TRACK)
    mesh = MeshGenerator(resolution=1).generate_mesh(track_data)
    solution = simulate(
        vehicle=vehicle, track_mesh=mesh, settings=settings.simulation_settings
    )
    return solution


def simulate_autocross(
    vehicle: Vehicle, settings: CompetitionSettings
) -> Solution:
    """
    Simulate the autocross event.

    Args:
        vehicle (Vehicle): The vehicle to simulate.
        settings (CompetitionSettings): Settings for the simulation.

    Returns:
        solution (Solution): The results of the simulation.
    """
    logging.info("Simulating autocross event...")
    track_data = settings.autocross_track
    mesh = MeshGenerator(resolution=1).generate_mesh(track_data)
    solution = simulate(
        vehicle=vehicle, track_mesh=mesh, settings=settings.simulation_settings
    )
    return solution


def simulate_endurance(
    vehicle: Vehicle, settings: CompetitionSettings
) -> Solution:
    """
    Simulate the endurance event.

    Args:
        vehicle (Vehicle): The vehicle to simulate.
        settings (CompetitionSettings): Settings for the simulation.

    Returns:
        solution (Solution): The results of the simulation.
    """
    logging.info("Simulating endurance event...")
    track_data = settings.autocross_track
    mesh = (
        MeshGenerator(resolution=1)
        .generate_mesh(track_data)
        .generate_endurance_mesh()
    )
    solution = simulate(
        vehicle=vehicle, track_mesh=mesh, settings=settings.simulation_settings
    )
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
