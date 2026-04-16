"""
This script evaluates the impact of changing the lambda coefficients.
"""

from usmlap.competition import Competition, CompetitionPoints, points_delta
from usmlap.model import LambdaCoefficients
from usmlap.plot import plot_points_bar_chart
from usmlap.simulation import SimulationSettings
from usmlap.simulation.solver import QuasiSteadyStateSolver as QSS
from usmlap.vehicle import Vehicle

competition = Competition()

vehicle = Vehicle.from_json("USM26")

configurations: dict[str, LambdaCoefficients] = {
    "+10% Longitudinal Grip": LambdaCoefficients(longitudinal_grip=1.1),
    "+10% Lateral Grip": LambdaCoefficients(lateral_grip=1.1),
    "+10% Motor Torque": LambdaCoefficients(motor_torque=1.1),
}

baseline_settings = SimulationSettings(solver=QSS)
baseline_points, _ = competition.simulate(vehicle, baseline_settings)

data: dict[str, CompetitionPoints] = {}

for name, coefficients in configurations.items():
    simulation_settings = SimulationSettings(solver=QSS, lambdas=coefficients)
    points, _ = competition.simulate(vehicle, simulation_settings)
    delta = points_delta(points, baseline_points)
    data[name] = delta

plot_points_bar_chart(data, title="Lambda Coefficients", y_label="Points Delta")
