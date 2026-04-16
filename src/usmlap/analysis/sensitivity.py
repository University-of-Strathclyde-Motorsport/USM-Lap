"""
This module contains code for points sensitivity analysis.
"""

from typing import Optional

from rich.progress import Progress

from usmlap.competition import Competition
from usmlap.simulation import SimulationSettings
from usmlap.vehicle import Parameter, Vehicle, get_new_vehicle

PARAMETER_DELTA_SCALAR = 0.0001
TASK_DESCRIPTION = "Evaluating sensitivity..."


def points_sensitivity(
    vehicle: Vehicle,
    settings: SimulationSettings,
    competition: Competition,
    parameter: type[Parameter],
    delta: Optional[tuple[float, float]] = None,
    normalise: bool = False,
) -> tuple[float, tuple[float, float]]:
    """
    Evaluate the points sensitivity of a vehicle parameter.

    Args:
        vehicle (Vehicle): The baseline vehicle to simulate.
        settings (SimulationSettings): Settings for the simulation.
        competition (Competition): The competition to simulate.
        parameter (Parameter): The parameter to analyse the sensitivity of.
        delta (Optional[tuple[float, float]]):
            The range of values to evaluate across.
            If not provided, the parameter uncertainty is used.
        normalise (bool): Whether to normalise the sensitivity.
            If `True`, the sensitivity is divided by the parameter delta.

    Returns:
        sensitivity (float): The points sensitivity of the parameter.
        delta (tuple[float, float]):
            The range over which the sensitivity was evaluated.
    """

    if not delta:
        if not parameter.uncertainty:
            raise ValueError(
                "Parameter has no uncertainty, unable to analyse sensitivity."
            )
        delta = (-parameter.uncertainty, parameter.uncertainty)

    baseline_value = parameter.get_value(vehicle)

    deltas: dict[str, float] = {"decreased": delta[0], "increased": delta[1]}
    results: dict[str, float] = {}
    with Progress(transient=True) as progress:
        task = progress.add_task(TASK_DESCRIPTION, total=2)
        for i, (label, value) in enumerate(deltas.items()):
            progress.update(task, description=f"{TASK_DESCRIPTION} ({i + 1}/2)")
            new_value = baseline_value + value
            modified_vehicle = get_new_vehicle(vehicle, parameter, new_value)
            points, _ = competition.simulate(modified_vehicle, settings)
            results[label] = sum(points.values())

    sensitivity = results["increased"] - results["decreased"]
    if normalise:
        sensitivity /= deltas["increased"] - deltas["decreased"]

    return sensitivity, delta
