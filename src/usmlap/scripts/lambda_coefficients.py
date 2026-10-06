"""
This script evaluates the impact of changing the lambda coefficients.
"""

from usmlap.competition.competition import (
    Competition,
    CompetitionPoints,
)
from usmlap.competition.points import points_delta
from usmlap.model.lambda_coefficients import LambdaCoefficients
from usmlap.plot.comparison import plot_points_bar_chart
from usmlap.simulation.settings import SimulationSettings
from usmlap.solver import QuasiSteadyStateSolver as QSS
from usmlap.vehicle.vehicle import Vehicle

competition = Competition()

vehicle = Vehicle.from_json("USM26")

configurations: dict[str, LambdaCoefficients] = {
    "+10% Longitudinal Grip": LambdaCoefficients(longitudinal_grip=1.1),
    "+10% Lateral Grip": LambdaCoefficients(lateral_grip=1.1),
    "+10% Motor Torque": LambdaCoefficients(motor_torque=1.1),
}

baseline_settings = SimulationSettings(solver=QSS)
baseline_results = competition.simulate(vehicle, baseline_settings)

data: dict[str, CompetitionPoints] = {}

for name, coefficients in configurations.items():
    simulation_settings = SimulationSettings(solver=QSS, lambdas=coefficients)
    results = competition.simulate(vehicle, simulation_settings)
    delta = points_delta(results.points, baseline_results.points)
    data[name] = delta

plot_points_bar_chart(data, title="Lambda Coefficients", y_label="Points Delta")
