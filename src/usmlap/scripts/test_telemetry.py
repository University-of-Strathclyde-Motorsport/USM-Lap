"""
This script is used for testing the telemetry module.
"""

from usmlap.competition.events import Autocross
from usmlap.plot.telemetry import plot_telemetry_channels
from usmlap.simulation.settings import QualityPresets
from usmlap.telemetry import TelemetrySolution
from usmlap.telemetry.channels.channel_functions import derivative, difference
from usmlap.telemetry.channels.data_channels import NodeTime, Position, Velocity
from usmlap.vehicle import Vehicle

vehicle = Vehicle.from_json("USM26")
event = Autocross(track_file="FS AutoX Germany 2012")
settings = QualityPresets.DRAFT
solution = event.simulate_event(vehicle, settings)

telemetry_solution = TelemetrySolution(
    vehicle=vehicle, solution=solution, solver=settings.solver
)

plot_telemetry_channels(
    telemetry_solution,
    [Position(), Velocity(), NodeTime(), derivative(Velocity(), NodeTime())],
)
