"""
This script analyses the sensitivities of a list of vehicle parameters.
"""

from textwrap import wrap

from rich import progress

from usmlap.analysis import points_sensitivity
from usmlap.competition import Competition
from usmlap.plot import plot_points_sensitivities
from usmlap.plot.points_sensitivities import PointsSensitivityData
from usmlap.simulation.settings import QualityPresets
from usmlap.vehicle import load_vehicle
from usmlap.vehicle.parameters import list_all_parameters

BASELINE_VEHICLE = "USM26.json"
QUALITY = QualityPresets.DRAFT
LIMIT_PARAMETERS = False

vehicle = load_vehicle(BASELINE_VEHICLE)
competition = Competition(simulate_efficiency=False)

parameters = list_all_parameters()
if LIMIT_PARAMETERS:
    parameters = parameters[:5]

sensitivities: list[PointsSensitivityData] = []

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
    datapoint = PointsSensitivityData(label=label, value=sensitivity)
    sensitivities.append(datapoint)

plot_points_sensitivities(
    sensitivities, title="Model Sensitivity to Parameter Uncertainties"
)
