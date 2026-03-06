"""
This module contains code for simulating a Formula Student competition.
"""

from dataclasses import dataclass, field

from rich import progress

from usmlap.simulation.simulation import SimulationSettings
from usmlap.simulation.solution import Solution
from usmlap.vehicle.vehicle import Vehicle

from . import events
from .events.event import EventInterface
from .results import CompetitionResults
from .settings import CompetitionSettings


@dataclass
class Competition(object):
    """
    Class for simulating a Formula Student competition.

    Attributes:
        simulation_settings (SimulationSettings):
            Settings for the simulation.
        competition_settings (CompetitionSettings):
            Settings for the competition.
    """

    simulation_settings: SimulationSettings
    competition_settings: CompetitionSettings
    acceleration: events.Acceleration = field(init=False)
    skidpad: events.Skidpad = field(init=False)
    autocross: events.Autocross = field(init=False)
    endurance: events.Endurance = field(init=False)

    @property
    def events(self) -> list[EventInterface]:
        return [self.acceleration, self.skidpad, self.autocross, self.endurance]

    def __post_init__(self) -> None:
        self.acceleration = self.create_event(events.Acceleration)
        self.skidpad = self.create_event(events.Skidpad)
        self.autocross = self.create_event(events.Autocross)
        self.endurance = self.create_event(events.Endurance)

    def create_event[T: EventInterface](self, event: type[T]) -> T:
        return event(
            simulation_settings=self.simulation_settings,
            competition_settings=self.competition_settings,
        )

    def simulate(self, vehicle: Vehicle) -> CompetitionResults:
        """
        Simulate a Formula Student competition.

        Args:
            vehicle (Vehicle): The vehicle to simulate.

        Returns:
            results (CompetitionResults): The results of the competition.
        """

        solutions: dict[str, Solution] = {}
        for event in progress.track(
            self.events, description="Simulating competition...", transient=True
        ):
            event_solution = event.simulate(vehicle)
            solutions[event.label] = event_solution

        return CompetitionResults(
            acceleration=solutions["acceleration"],
            skidpad=solutions["skidpad"],
            autocross=solutions["autocross"],
            endurance=solutions["endurance"],
        )
