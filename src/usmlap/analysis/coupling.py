"""
This module contains code for analysing the coupling between two parameters.
"""

from dataclasses import dataclass, field

import matplotlib.pyplot as plt
from rich import progress

from usmlap.competition.competition import Competition
from usmlap.vehicle.parameters import Parameter
from usmlap.vehicle.vehicle import Vehicle

from .sensitivity import points_sensitivity
from .sweep_1d import SweepSettings


@dataclass
class CouplingResults(object):
    """
    The results of a coupling analysis.

    Attributes:
        sweep_parameter (Parameter):
            The parameter being swept.
        coupled_parameter (Parameter):
            The parameter being evaluated.
        data (dict[float, float]):
            A dictionary containing swept parameter values
            and the corresponding sensitivities of the coupled parameter.
    """

    sweep_parameter: type[Parameter]
    coupled_parameter: type[Parameter]
    data: dict[float, float] = field(default_factory=lambda: {})

    def plot(self) -> None:
        plt.plot(list(self.data.keys()), list(self.data.values()))
        plt.title(
            f"Coupling - {self.sweep_parameter.name} and {self.coupled_parameter.name}"
        )
        plt.xlabel(self.sweep_parameter.get_name_with_unit())
        plt.ylabel(f"{self.coupled_parameter.name} Sensitivity")
        plt.grid()
        plt.show()


def coupling(
    baseline_vehicle: Vehicle,
    competition: Competition,
    sweep_settings: SweepSettings,
    coupled_parameter: type[Parameter],
) -> CouplingResults:
    """
    Carry out a coupling analysis between two parameters.

    Args:
        baseline_vehicle (Vehicle):
            The vehicle to simulate.
        sweep_settings (SweepSettings):
            Settings for sweeping the first parameter.
        coupled_parameter (type[Parameter]):
            The parameter to evaluate the sensitivity of.

    Returns:
        coupling_results (CouplingResults):
            The results of the coupling analysis.
    """
    coupling_results = CouplingResults(
        sweep_parameter=sweep_settings.parameter,
        coupled_parameter=coupled_parameter,
    )
    for value, vehicle in progress.track(
        sweep_settings.get_vehicles(baseline_vehicle),
        description=f"Sweeping {sweep_settings.parameter.name}...",
        transient=True,
        total=sweep_settings.number_of_steps,
    ):
        sensitivity = points_sensitivity(
            vehicle=vehicle,
            competition=competition,
            parameter=coupled_parameter,
        )
        coupling_results.data[value] = sensitivity
    return coupling_results
