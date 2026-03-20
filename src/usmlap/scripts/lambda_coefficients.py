"""
This script evaluates the impact of changing the lambda coefficients.
"""

from usmlap.competition.competition import Competition, CompetitionSettings
from usmlap.competition.points import CompetitionPoints, points_delta
from usmlap.plot.comparison import plot_points_bar_chart
from usmlap.simulation.lambda_coefficients import LambdaCoefficients
from usmlap.simulation.simulation import SimulationSettings
from usmlap.simulation.solver.quasi_steady_state import (
    QuasiSteadyStateSolver as QSS,
)
from usmlap.vehicle.vehicle import load_vehicle

competition_settings = CompetitionSettings(dataset="FSG 2025 Hybrid")
competition = Competition(competition_settings)

vehicle_file = "USM26.json"
vehicle = load_vehicle(vehicle_file)

configurations: dict[str, LambdaCoefficients] = {
    "+10% Longitudinal Grip": LambdaCoefficients(longitudinal_grip=1.1),
    "+10% Lateral Grip": LambdaCoefficients(lateral_grip=1.1),
    "+10% Motor Torque": LambdaCoefficients(motor_torque=1.1),
}

baseline_settings = SimulationSettings(solver=QSS)
baseline_points = competition.simulate(vehicle, baseline_settings)

data: dict[str, CompetitionPoints] = {}

for name, coefficients in configurations.items():
    simulation_settings = SimulationSettings(solver=QSS, lambdas=coefficients)
    points = competition.simulate(vehicle, simulation_settings)
    delta = points_delta(points, baseline_points)
    data[name] = delta

plot_points_bar_chart(data, title="Lambda Coefficients", y_label="Points Delta")
