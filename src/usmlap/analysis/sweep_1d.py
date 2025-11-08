"""
This module contains code for carrying out a 1D sweep of a parameter.
"""

from typing import Generator
from dataclasses import dataclass, field
import numpy as np

from vehicle.vehicle import Vehicle
from vehicle.parameters import Parameter
from simulation.simulation import SimulationSettings
from simulation.competition import simulate_competition
from simulation.points.points import calculate_points

import matplotlib.pyplot as plt


@dataclass
class SweepSettings(object):
    """
    Settings for a 1D sweep of a parameter.

    Attributes:
        parameter (Parameter): The parameter to sweep.
        start_value (float): The start value of the sweep.
        end_value (float): The end value of the sweep.
        number_of_steps (int): The number of steps in the sweep.
    """

    parameter: Parameter
    start_value: float
    end_value: float
    number_of_steps: int

    @property
    def values(self) -> list[float]:
        return np.linspace(
            self.start_value, self.end_value, self.number_of_steps
        ).tolist()

    def get_vehicles(
        self, baseline_vehicle: Vehicle
    ) -> Generator[tuple[float, Vehicle]]:
        """
        Generate a list of vehicles for a sweep.

        Args:
            baseline_vehicle (Vehicle): The baseline vehicle to use.

        Yields:
            result (tuple[float, Vehicle]):
                A tuple containing the modified parameter value
                and the corresponding vehicle.
        """
        for value in self.values:
            vehicle = self.parameter.get_new_vehicle(
                baseline_vehicle=baseline_vehicle, value=value
            )
            yield (value, vehicle)


@dataclass
class SweepResults(object):
    """
    The results of a 1D sweep of a parameter.

    Attributes:
        parameter (Parameter): The parameter being swept.
        data (dict[float, float]):
            A dictionary containing parameter values
            and the corresponding points scored.
    """

    parameter: Parameter
    data: dict[float, float] = field(default_factory=lambda: {})

    def plot(self) -> None:
        plt.plot(list(self.data.keys()), list(self.data.values()))
        plt.title(f"Points Sensitivity - {self.parameter.name}")
        plt.xlabel(self.parameter.get_name_with_unit())
        plt.ylabel("Points")
        plt.grid()
        plt.show()


def sweep_1d(
    baseline_vehicle: Vehicle,
    sweep_settings: SweepSettings,
    simulation_settings: SimulationSettings,
) -> SweepResults:
    """
    Carries out a 1D sweep of a parameter.

    Args:
        vehicle (Vehicle): The vehicle to simulate.
        sweep_settings (SweepSettings): Settings for the sweep.
        simulation_settings (SimulationSettings): Settings for the simulation.
    """
    sweep_results = SweepResults(parameter=sweep_settings.parameter)

    for value, vehicle in sweep_settings.get_vehicles(baseline_vehicle):
        results = simulate_competition(vehicle, simulation_settings)
        points = calculate_points(results)
        sweep_results.data[value] = points.total

    return sweep_results
