"""
This script simulates the skidpad event.
"""

from usmlap.competition.events import Skidpad
from usmlap.plot import plot_apexes
from usmlap.simulation import LambdaCoefficients, SimulationSettings
from usmlap.vehicle import load_vehicle

skidpad = Skidpad()

vehicle_file = "USM26.json"
vehicle = load_vehicle(vehicle_file)

lambda_coefficients = LambdaCoefficients(lateral_grip=1.2)
simulation_settings = SimulationSettings(lambdas=lambda_coefficients)

solution = skidpad.simulate_event(vehicle, simulation_settings)
plot_apexes(solution)
