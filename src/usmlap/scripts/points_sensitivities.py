"""
This script analyses the sensitivities of a list of vehicle parameters.
"""

from pathlib import Path
from textwrap import wrap

from rich import progress

from usmlap.analysis.sensitivity import points_sensitivity
from usmlap.competition.competition import Competition
from usmlap.plot.points_sensitivities import (
    PointsSensitivityData,
    plot_points_sensitivities,
)
from usmlap.simulation.settings import SimSettings
from usmlap.vehicle.parameters import list_all_parameters
from usmlap.vehicle.vehicle import Vehicle

BASELINE_VEHICLE = "USM26"
settings = SimSettings.from_yaml(Path("sims/basic_simulation.yaml"))
LIMIT_PARAMETERS = False

vehicle = Vehicle.from_json(BASELINE_VEHICLE)
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
        vehicle,
        settings,
        competition,
        parameter,
    )
    wrapped_name = "\n".join(wrap(parameter.name, 12))
    upper_value = parameter.append_unit(f"{deltas[1]:+}")
    lower_value = parameter.append_unit(f"{deltas[0]:+}")
    label = f"{wrapped_name}\n{upper_value}\n{lower_value}"
    datapoint = PointsSensitivityData(label=label, value=sensitivity)
    sensitivities.append(datapoint)

plot_points_sensitivities(
    sensitivities,
    title="Model Sensitivity to Parameter Uncertainties",
    max_results=15,
)
