"""
This module contains code for sweeping through a list of vehicles."""

from collections.abc import Collection

from rich.progress import Progress

from usmlap.competition.competition import Competition, CompetitionResults
from usmlap.simulation.settings import SimulationSettings
from usmlap.vehicle.vehicle import Vehicle


def sweep_vehicles(
    vehicles: Collection[Vehicle],
    settings: SimulationSettings,
) -> dict[str, CompetitionResults]:
    """
    Simulate a list of vehicles."""
    competition = Competition()
    results: dict[str, CompetitionResults] = {}

    with Progress(transient=True) as progress:
        task = progress.add_task("Simulating vehicles...", total=len(vehicles))

        for vehicle in vehicles:
            task_description = f"Simulating vehicle {vehicle.label}..."
            progress.update(task, description=task_description)

            result = competition.simulate(vehicle, settings)
            results[vehicle.label] = result

    return results
