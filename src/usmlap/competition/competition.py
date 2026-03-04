"""
This module contains code for simulating a Formula Student competition.
"""

from dataclasses import dataclass, field

from usmlap.simulation.simulation import SimulationSettings
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

        acceleration_solution = self.acceleration.simulate(vehicle)
        skidpad_solution = self.skidpad.simulate(vehicle)
        autocross_solution = self.autocross.simulate(vehicle)
        endurance_solution = self.endurance.simulate(vehicle)

        return CompetitionResults(
            acceleration=acceleration_solution,
            skidpad=skidpad_solution,
            autocross=autocross_solution,
            endurance=endurance_solution,
        )
