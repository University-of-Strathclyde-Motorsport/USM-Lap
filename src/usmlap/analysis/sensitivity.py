"""
This module contains code for points sensitivity analysis.
"""

from dataclasses import dataclass

from usmlap.competition.competition import Competition
from usmlap.competition.points.points import calculate_points
from usmlap.vehicle.parameters import Parameter, get_new_vehicle
from usmlap.vehicle.vehicle import Vehicle

PARAMETER_DELTA_SCALAR = 0.0001


def points_sensitivity(
    vehicle: Vehicle, competition: Competition, parameter: Parameter
) -> float:
    """
    Evaluate the points sensitivity of a vehicle parameter.

    Args:
        vehicle (Vehicle): The baseline vehicle to simulate.
        competition (Competition): The competition to simulate.
        parameter (Parameter): The parameter to analyse the sensitivity of.

    Returns:
        sensitivity (float): The points sensitivity of the parameter,
            measured in points per unit.
    """
    analysis = SensitivityAnalysis(vehicle, competition, parameter)
    sensitivity = analysis.get_sensitivity()
    return sensitivity


@dataclass
class SensitivityAnalysis(object):
    """
    Class for carrying out sensitivity analysis.
    """

    baseline_vehicle: Vehicle
    competition: Competition
    parameter: Parameter

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

        for direction, vehicle in vehicles.items():
            results = self.competition.simulate(vehicle=vehicle)
            points = calculate_points(results=results)
            total_points[direction] = points.total

        points_delta = total_points["increased"] - total_points["decreased"]
        sensitivity = points_delta / (2 * self.parameter_delta)
        return sensitivity
