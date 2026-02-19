"""
This module contains code for comparing two or more distinct vehicles.
"""

from typing import Generator

from simulation.simulation import SimulationSettings, simulate
from simulation.solution import Solution
from track.mesh import Mesh
from vehicle.vehicle import Vehicle


class ComparisonResults(object):
    """
    Data structure containing the results of a comparison simulation.
    """

    _vehicles: list[Vehicle]
    _solutions: list[Solution]

    def __init__(self) -> None:
        self._vehicles = []
        self._solutions = []

    def add_result(self, vehicle: Vehicle, solution: Solution) -> None:
        """
        Add a result to the comparison.

        Args:
            vehicle (Vehicle): The vehicle that was simulated.
            solution (Solution): The solution of the simulation.
        """
        self._vehicles.append(vehicle)
        self._solutions.append(solution)

    def __iter__(self) -> Generator[tuple[Vehicle, Solution]]:
        for vehicle, solution in zip(self._vehicles, self._solutions):
            yield vehicle, solution

    def get_vehicles(self) -> list[Vehicle]:
        """
        Get a list of the vehicles that were simulated.

        Returns:
            vehicles (list[Vehicle]): The vehicles that were simulated.
        """
        return self._vehicles

    def get_solutions(self) -> list[Solution]:
        """
        Get a list of the solutions that were simulated.

        Returns:
            solutions (list[Solution]): The solutions to the simulations.
        """
        return self._solutions


def compare_vehicles(
    vehicles: list[Vehicle], mesh: Mesh, simulation_settings: SimulationSettings
) -> ComparisonResults:
    """
    Run simulations for a list of vehicles and return the results.
    """

    results = ComparisonResults()

    for vehicle in vehicles:
        solution = simulate(vehicle, mesh, simulation_settings)
        results.add_result(vehicle, solution)

    return results
