"""
This module contains code for simulating a Formula Student competition.
"""

from dataclasses import InitVar, dataclass, field

from rich.progress import Progress

from usmlap.simulation.simulation import SimulationSettings
from usmlap.simulation.solution import Solution
from usmlap.vehicle.vehicle import Vehicle

from .events.acceleration import Acceleration
from .events.autocross import Autocross
from .events.endurance import Endurance
from .events.event import EventInterface
from .events.skidpad import Skidpad
from .points import CompetitionData, CompetitionPoints

DEFAULT_AUTOCROSS_TRACK = "FS AutoX Germany 2012.xlsx"
DEFAULT_COMPETITION_DATASET = "FSG 2025"


@dataclass
class CompetitionSettings(object):
    """
    Settings for simulating a Formula Student competition.

    Attributes:
        autocross_track (str): Track to use for autocross and endurance events.
        simulate_acceleration (bool): Whether to simulate the acceleration event.
        simulate_skidpad (bool): Whether to simulate the skidpad event.
        simulate_autocross (bool): Whether to simulate the autocross event.
        simulate_endurance (bool): Whether to simulate the endurance event.
    """

    autocross_track: str = DEFAULT_AUTOCROSS_TRACK
    simulate_acceleration: bool = True
    simulate_skidpad: bool = True
    simulate_autocross: bool = True
    simulate_endurance: bool = True
    dataset: InitVar[str] = field(default=DEFAULT_COMPETITION_DATASET)
    competition_data: CompetitionData = field(init=False)

    def __post_init__(self, dataset: str) -> None:
        self.competition_data = CompetitionData.from_library(dataset)


type CompetitionResults = dict[str, Solution]


@dataclass
class Competition(object):
    """
    Class for simulating a Formula Student competition.

    Attributes:
        settings: Settings for the competition.
        events: List of events to simulate.
    """

    settings: CompetitionSettings
    events: list[EventInterface] = field(init=False, default_factory=list)

    def __post_init__(self) -> None:
        self._create_events()

    def _add_event(self, event: EventInterface) -> None:
        self.events.append(event)

    def _create_events(self) -> None:
        """
        Create competition events.
        """

        with Progress(transient=True) as progress:
            task = progress.add_task("Setting up events...")
            if self.settings.simulate_acceleration:
                progress.update(task, description="Setting up Acceleration...")
                acceleration = Acceleration(
                    competition_data=self.settings.competition_data
                )
                self._add_event(acceleration)

            if self.settings.simulate_skidpad:
                progress.update(task, description="Setting up Skidpad...")
                skidpad = Skidpad(
                    competition_data=self.settings.competition_data
                )
                self._add_event(skidpad)

            if self.settings.simulate_autocross:
                progress.update(task, description="Setting up Autocross...")
                autocross = Autocross(
                    track_file=self.settings.autocross_track,
                    competition_data=self.settings.competition_data,
                )
                self._add_event(autocross)

            if self.settings.simulate_endurance:
                progress.update(task, description="Setting up Endurance...")
                endurance = Endurance(
                    track_file=self.settings.autocross_track,
                    competition_data=self.settings.competition_data,
                )
                self._add_event(endurance)

    def simulate(
        self, vehicle: Vehicle, settings: SimulationSettings
    ) -> CompetitionPoints:
        """
        Simulate a Formula Student competition.

        Args:
            vehicle (Vehicle): The vehicle to simulate.
            settings (SimulationSettings): Settings for the simulation.

        Returns:
            competition_points (CompetitionPoints):
                Dictionary of points scored in all simulated events.
        """

        competition_points: CompetitionPoints = {}

        with Progress(transient=True) as progress:
            task = progress.add_task(
                "Simulating competition...", total=len(self.events)
            )

            for event in self.events:
                progress.update(
                    task, description=f"Simulating {event.label}..."
                )

                event_points = event.simulate_event(vehicle)
                competition_points.update(event_points)

                progress.advance(task)

        return competition_points
