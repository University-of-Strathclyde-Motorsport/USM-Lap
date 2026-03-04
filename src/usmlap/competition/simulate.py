"""
This module contains code for simulating a Formula Student competition.
"""

from dataclasses import dataclass, field

from usmlap.simulation.simulation import SimulationSettings
from usmlap.simulation.solution import Solution
from usmlap.vehicle.vehicle import Vehicle

from .events import EVENTS
from .events.event import EventInterface
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
    events: dict[str, EventInterface] = field(init=False)

    def __post_init__(self) -> None:
        self.events = {
            event_name: self.create_event(event)
            for event_name, event in EVENTS.items()
        }

    def create_event(self, event: type[EventInterface]) -> EventInterface:
        return event(
            simulation_settings=self.simulation_settings,
            competition_settings=self.competition_settings,
        )

    def simulate(self, vehicle: Vehicle) -> dict[str, Solution]:
        return {
            event_name: event.simulate(vehicle=vehicle)
            for event_name, event in self.events.items()
        }
