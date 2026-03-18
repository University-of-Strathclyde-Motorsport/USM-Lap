"""
This module contains code for points sensitivity analysis.
"""

from dataclasses import dataclass

from rich.progress import Progress

from usmlap.competition.competition import Competition
from usmlap.simulation.simulation import SimulationSettings
from usmlap.vehicle.parameters import Parameter, get_new_vehicle
from usmlap.vehicle.vehicle import Vehicle

PARAMETER_DELTA_SCALAR = 0.0001
TASK_DESCRIPTION = "Evaluating sensitivity..."


def points_sensitivity(
    vehicle: Vehicle,
    settings: SimulationSettings,
    competition: Competition,
    parameter: type[Parameter],
) -> float:
    """
    Evaluate the points sensitivity of a vehicle parameter.

    Args:
        vehicle (Vehicle): The baseline vehicle to simulate.
        settings (SimulationSettings): Settings for the simulation.
        competition (Competition): The competition to simulate.
        parameter (Parameter): The parameter to analyse the sensitivity of.

    Returns:
        sensitivity (float): The points sensitivity of the parameter,
            measured in points per unit.
    """
    analysis = SensitivityAnalysis(vehicle, settings, competition, parameter)
    sensitivity = analysis.get_sensitivity()
    return sensitivity


@dataclass
class SensitivityAnalysis(object):
    """
    Class for carrying out sensitivity analysis.
    """

    baseline_vehicle: Vehicle
    settings: SimulationSettings
    competition: Competition
    parameter: type[Parameter]

    @property
    def baseline_value(self) -> float:
        return self.parameter.get_value(self.baseline_vehicle)

    @property
    def parameter_delta(self) -> float:
        return self.baseline_value * PARAMETER_DELTA_SCALAR

    @property
    def increased_value_vehicle(self) -> Vehicle:
        new_value = self.baseline_value + self.parameter_delta
        return get_new_vehicle(self.baseline_vehicle, self.parameter, new_value)

    @property
    def decreased_value_vehicle(self) -> Vehicle:
        new_value = self.baseline_value - self.parameter_delta
        return get_new_vehicle(self.baseline_vehicle, self.parameter, new_value)

    def get_sensitivity(self) -> float:
        vehicles = {
            "increased": self.increased_value_vehicle,
            "decreased": self.decreased_value_vehicle,
        }
        total_points: dict[str, float] = {}

        with Progress(transient=True) as progress:
            task = progress.add_task(TASK_DESCRIPTION, total=2)
            for i, (direction, vehicle) in enumerate(vehicles.items()):
                progress.update(
                    task, description=f"{TASK_DESCRIPTION} ({i + 1}/2)"
                )
                _, points = self.competition.simulate(vehicle, self.settings)
                total_points[direction] = sum(points.values())
                progress.advance(task)

        points_delta = total_points["increased"] - total_points["decreased"]
        sensitivity = points_delta / (2 * self.parameter_delta)
        return sensitivity
