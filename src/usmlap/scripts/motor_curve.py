"""
This script plots a map of motor performance.
"""

from pathlib import Path

from usmlap.plot.component.motor import plot_motor_curve
from usmlap.vehicle.vehicle import Vehicle

vehicle = Vehicle.from_file(Path(r"data\vehicles\USM26.json"))
powertrain = vehicle.powertrain
plot_motor_curve(powertrain)
