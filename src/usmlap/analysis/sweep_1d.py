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
from usmlap.simulation.simulation import SimulationSettings
from usmlap.vehicle.parameters import Parameter, get_new_vehicle
from usmlap.vehicle.vehicle import Vehicle


@dataclass
class SweepSettings(object):
    """
    Settings for a 1D sweep of a parameter.

    Attributes:
        parameter (type[Parameter[float]]): The parameter to sweep.
        start_value (float): The start value of the sweep.
        end_value (float): The end value of the sweep.
        number_of_steps (int): The number of steps in the sweep.
    """

    parameter: type[Parameter[float]]
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
        parameter (type[Parameter[float]]): The parameter being swept.
        data (dict[float, float]):
            A dictionary containing parameter values
            and the corresponding points scored.
    """

    parameter: type[Parameter[float]]
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
    simulation_settings: SimulationSettings,
    competition: Competition,
    sweep_settings: SweepSettings,
) -> SweepResults:
    """
    Carry out a 1D sweep of a parameter.

    Args:
        baseline_vehicle (Vehicle): The vehicle to simulate.
        simulation_settings (SimulationSettings): Settings for the simulation.
        competition (Competition): The competition to simulate.
        sweep_settings (SweepSettings): Settings for the sweep.

    Returns:
        sweep_results (SweepResults): The results of the sweep.
    """
    sweep_results = SweepResults(parameter=sweep_settings.parameter)

    for value, vehicle in progress.track(
        sweep_settings.get_vehicles(baseline_vehicle),
        description=f"Sweeping {sweep_settings.parameter.name}...",
        transient=True,
        total=sweep_settings.number_of_steps,
    ):
        logging.info(
            f"Simulating vehicle with {sweep_settings.parameter.name} = {value}"
        )
        _, points = competition.simulate(vehicle, simulation_settings)
        sweep_results.data[value] = sum(points.values())

    return sweep_results
