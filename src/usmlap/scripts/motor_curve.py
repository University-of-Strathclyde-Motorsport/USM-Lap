"""
This script plots a map of motor performance.
"""

from usmlap.plot.motor import plot_motor_curve
from usmlap.vehicle.vehicle import Vehicle

vehicle = Vehicle.from_json("USM26")
powertrain = vehicle.powertrain
plot_motor_curve(powertrain)
