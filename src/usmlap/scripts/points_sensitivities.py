"""
This script analyses the sensitivities of a list of vehicle parameters.
"""

from textwrap import wrap

from rich import progress

from usmlap.analysis import points_sensitivity
from usmlap.competition import Competition
from usmlap.plot import plot_points_sensitivities
from usmlap.simulation.settings import QualityPresets
from usmlap.vehicle import load_vehicle
from usmlap.vehicle.parameters import (
    CurbMass,
    LiftCoefficient,
    MotorControllerResistance,
    list_all_parameters,
)

BASELINE_VEHICLE = "USM26.json"
QUALITY = QualityPresets.DRAFT

vehicle = load_vehicle(BASELINE_VEHICLE)
competition = Competition()

# parameters = [MotorControllerResistance, LiftCoefficient, CurbMass]
parameters = list_all_parameters()
sensitivities: dict[str, float] = {}


for parameter in progress.track(parameters, "Evaluating parameters..."):
    if not parameter.implemented:
        continue
    if not parameter.uncertainty:
        continue
    sensitivity, deltas = points_sensitivity(
        vehicle, QUALITY, competition, parameter
    )
    wrapped_name = "\n".join(wrap(parameter.name, 12))
    upper_value = parameter.append_unit(f"{deltas[1]:+}")
    lower_value = parameter.append_unit(f"{deltas[0]:+}")
    label = f"{wrapped_name}\n{upper_value}\n{lower_value}"
    sensitivities[label] = sensitivity

plot_points_sensitivities(
    sensitivities, title="Sensitivities of Parameter Uncertainties"
)
