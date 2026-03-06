"""
This module contains code for carrying out a 1D sweep of a parameter.
"""

import logging
from dataclasses import dataclass, field
from typing import Generator

import matplotlib.pyplot as plt
import numpy as np
from rich import progress

from usmlap.competition.competition import Competition
from usmlap.competition.points.points import calculate_points
from usmlap.vehicle.parameters import Parameter, get_new_vehicle
from usmlap.vehicle.vehicle import Vehicle


@dataclass
class SweepSettings(object):
    """
    Settings for a 1D sweep of a parameter.

    Attributes:
        parameter (type[Parameter]): The parameter to sweep.
        start_value (float): The start value of the sweep.
        end_value (float): The end value of the sweep.
        number_of_steps (int): The number of steps in the sweep.
    """

    parameter: type[Parameter]
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
            vehicle = get_new_vehicle(baseline_vehicle, self.parameter, value)
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

    parameter: type[Parameter]
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
    competition: Competition,
    sweep_settings: SweepSettings,
) -> SweepResults:
    """
    Carry out a 1D sweep of a parameter.

    Args:
        baseline_vehicle (Vehicle): The vehicle to simulate.
        sweep_settings (SweepSettings): Settings for the sweep.
        competition_settings (CompetitionSettings):
            Settings for the competition.

    Returns:
        sweep_results (SweepResults): The results of the sweep.
    """
    sweep_results = SweepResults(parameter=sweep_settings.parameter)

    sweep_vehicles = list(sweep_settings.get_vehicles(baseline_vehicle))
    for value, vehicle in progress.track(
        sweep_vehicles,
        description=f"Sweeping parameter {sweep_settings.parameter.name}",
    ):
        logging.info(
            f"Simulating vehicle with {sweep_settings.parameter.name} = {value}"
        )
        results = competition.simulate(vehicle)
        points = calculate_points(results)
        sweep_results.data[value] = points.total

    return sweep_results
