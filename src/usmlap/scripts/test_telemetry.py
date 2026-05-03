"""
This script is used for testing the telemetry module.
"""

from pint import UnitRegistry

from usmlap.competition.events import Autocross
from usmlap.plot.telemetry import plot_channels
from usmlap.simulation.settings import QualityPresets
from usmlap.telemetry.channel.functions import derivative, negate, power
from usmlap.telemetry.channel.library import NodeTime, Position, Velocity
from usmlap.vehicle import Vehicle

vehicle = Vehicle.from_json("USM26")
event = Autocross(track_file="FS AutoX Germany 2012")
settings = QualityPresets.DRAFT
telemetry_solution = event.simulate_event(vehicle, settings)


plot_channels(
    telemetry_solution,
    [
        Position(),
        Velocity(),
        NodeTime(),
        negate(Velocity(), label="Test Label", unit=UnitRegistry().hour),
        derivative(Position(label="Position (Mine!)"), NodeTime()),
        power(Velocity(), 2.5),
    ],
    title="Test Telemetry",
    show_sectors=True,
    y_label_rotation="vertical",
)
