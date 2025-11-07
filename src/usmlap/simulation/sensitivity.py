"""
This module contains code for points sensitivity analysis.
"""

from vehicle.vehicle import Vehicle
from vehicle.parameters import Parameter
from simulation.competition import Competition
from simulation.points.points import calculate_points

PARAMETER_DELTA_SCALAR = 0.0001


class SensitivityAnalysis(object):
    """
    Class for carrying out sensitivity analysis.
    """

    def __init__(self, baseline_vehicle: Vehicle, parameter: Parameter) -> None:
        self.baseline_vehicle = baseline_vehicle
        self.parameter = parameter

    @property
    def baseline_value(self) -> float:
        return self.parameter.get_value(self.baseline_vehicle)

    @property
    def parameter_delta(self) -> float:
        return self.baseline_value * PARAMETER_DELTA_SCALAR

    @property
    def increased_value_vehicle(self) -> Vehicle:
        return self.parameter.get_new_vehicle(
            baseline_vehicle=self.baseline_vehicle,
            value=self.baseline_value + self.parameter_delta,
        )

    @property
    def decreased_value_vehicle(self) -> Vehicle:
        return self.parameter.get_new_vehicle(
            baseline_vehicle=self.baseline_vehicle,
            value=self.baseline_value - self.parameter_delta,
        )

    def get_sensitivity(self) -> float:
        vehicles = {
            "increased": self.increased_value_vehicle,
            "decreased": self.decreased_value_vehicle,
        }
        track_file = "D:/Repositories/USM-Lap/appdata/library/tracks/FS AutoX Germany 2012.xlsx"
        total_points: dict[str, float] = {}

        for direction, vehicle in vehicles.items():
            competition = Competition(
                vehicle=vehicle, autocross_track=track_file
            )
            results = competition.simulate()
            points = calculate_points(results=results)
            total_points[direction] = points.total

        points_delta = total_points["increased"] - total_points["decreased"]
        sensitivity = points_delta / (2 * self.parameter_delta)
        return sensitivity
