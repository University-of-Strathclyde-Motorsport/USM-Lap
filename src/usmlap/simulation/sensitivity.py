"""
This module contains code for points sensitivity analysis.
"""

from dataclasses import dataclass

from usmlap.simulation.competition import (
    CompetitionSettings,
    simulate_competition,
)
from usmlap.simulation.points.points import calculate_points
from usmlap.vehicle.parameters import Parameter, get_new_vehicle
from usmlap.vehicle.vehicle import Vehicle

PARAMETER_DELTA_SCALAR = 0.0001


def points_sensitivity(
    vehicle: Vehicle, parameter: Parameter, settings: CompetitionSettings
) -> float:
    baseline_value = parameter.get_value(vehicle)
    parameter_delta = baseline_value * PARAMETER_DELTA_SCALAR

    increased_value = baseline_value + parameter_delta
    increased_vehicle = get_new_vehicle(vehicle, parameter, increased_value)
    increased_results = simulate_competition(increased_vehicle, settings)
    increased_points = calculate_points(increased_results).total

    decreased_value = baseline_value - parameter_delta
    decreased_vehicle = get_new_vehicle(vehicle, parameter, decreased_value)
    decreased_results = simulate_competition(decreased_vehicle, settings)
    decreased_points = calculate_points(decreased_results).total

    points_delta = increased_points - decreased_points
    sensitivity = points_delta / (2 * parameter_delta)
    return sensitivity


@dataclass
class SensitivityAnalysis(object):
    """
    Class for carrying out sensitivity analysis.
    """

    baseline_vehicle: Vehicle
    parameter: Parameter
    competition_settings: CompetitionSettings

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
            results = simulate_competition(
                vehicle=vehicle, settings=self.competition_settings
            )
            points = calculate_points(results=results)
            total_points[direction] = points.total

        points_delta = total_points["increased"] - total_points["decreased"]
        sensitivity = points_delta / (2 * self.parameter_delta)
        return sensitivity
