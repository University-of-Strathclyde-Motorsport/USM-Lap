"""
This script simulates the skidpad event.
"""

from usmlap.competition.events.skidpad import Skidpad
from usmlap.plot.apex import plot_apexes
from usmlap.simulation.lambda_coefficients import LambdaCoefficients
from usmlap.simulation.simulation import SimulationSettings
from usmlap.vehicle.vehicle import load_vehicle

skidpad = Skidpad()

vehicle_file = "USM26.json"
vehicle = load_vehicle(vehicle_file)

lambda_coefficients = LambdaCoefficients(lateral_grip=1.2)
simulation_settings = SimulationSettings(lambdas=lambda_coefficients)

solution = skidpad.simulate_event(vehicle, simulation_settings)
plot_apexes(solution)
