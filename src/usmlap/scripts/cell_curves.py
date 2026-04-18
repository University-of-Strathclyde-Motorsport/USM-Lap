"""
This script plots the parameters of a cell.
"""

from usmlap.plot import plot_cell_parameters
from usmlap.vehicle.powertrain import Accumulator

accumulator = Accumulator.from_json("USM26")
plot_cell_parameters(accumulator)
