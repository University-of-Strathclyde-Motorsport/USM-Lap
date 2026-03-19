"""
This module contains code for comparing two or more distinct vehicles.
"""

from typing import Generator

from usmlap.competition.competition import Competition, CompetitionPoints
from usmlap.simulation.simulation import SimulationSettings
from usmlap.vehicle.vehicle import Vehicle


class ComparisonResults(object):
    """
    Data structure containing the results of a comparison simulation.
    """

    _vehicles: list[Vehicle]
    _points: list[CompetitionPoints]

    def __init__(self) -> None:
        self._vehicles = []
        self._points = []

    def add_result(self, vehicle: Vehicle, points: CompetitionPoints) -> None:
        """
        Add a result to the comparison.

        Args:
            vehicle (Vehicle): The vehicle that was simulated.
            points (CompetitionPoints): Competition points for the vehicle.
        """
        self._vehicles.append(vehicle)
        self._points.append(points)

    def __iter__(self) -> Generator[tuple[Vehicle, CompetitionPoints]]:
        for vehicle, points in zip(self._vehicles, self._points):
            yield vehicle, points

    def get_vehicles(self) -> list[Vehicle]:
        """
        Get a list of the vehicles that were simulated.

        Returns:
            vehicles (list[Vehicle]): The vehicles that were simulated.
        """
        return self._vehicles

    def get_points(self) -> list[CompetitionPoints]:
        """
        Get a list of results.

        Returns:
            points (list[CompetitionPoints]): The results to the simulations.
        """
        return self._points

    def get_vehicle_labels(self) -> list[str]:
        """
        Get a list of labels for the vehicles that were simulated.

        Returns:
            labels (list[str]): The labels for the vehicles.
        """

        return [vehicle.metadata.print_name for vehicle in self._vehicles]


def compare_vehicles(
    vehicles: list[Vehicle],
    simulation_settings: SimulationSettings,
    competition: Competition,
) -> ComparisonResults:
    """
    Run simulations for a list of vehicles and return the results.
    """

    results = ComparisonResults()

    for vehicle in vehicles:
        points = competition.simulate(vehicle, simulation_settings)
        results.add_result(vehicle, points)

    return results
