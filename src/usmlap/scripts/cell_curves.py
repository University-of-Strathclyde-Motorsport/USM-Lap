"""
This script plots the parameters of a cell.
"""

from usmlap.plot import plot_cell_parameters
from usmlap.vehicle.powertrain import Cell

cell = Cell.from_json("molicel_P30b")
plot_cell_parameters(cell)
