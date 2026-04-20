"""
This script plots the parameters of a cell.
"""

import matplotlib.pyplot as plt

from usmlap.plot import plot_cell_parameters
from usmlap.plot.cell import _plot_resistance
from usmlap.vehicle.powertrain import Accumulator, Cell

# accumulator = Accumulator.from_json("USM26")
# plot_cell_parameters(accumulator)


cells = [Cell.from_json("sony_VTC6"), Cell.from_json("molicel_P30b")]

_, axs = plt.subplots(ncols=2)

for cell, ax in zip(cells, axs):
    _plot_resistance(cell, ax, title=cell.print_name, y_limits=(0, 30))

plt.show()
