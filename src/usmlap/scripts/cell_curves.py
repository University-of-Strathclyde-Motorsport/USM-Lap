"""
This script plots the parameters of a cell.
"""

from pathlib import Path

import matplotlib.pyplot as plt

from usmlap.plot.component.cell import _plot_resistance
from usmlap.vehicle.powertrain.cell import Cell

# accumulator = Accumulator.from_file("USM26")
# plot_cell_parameters(accumulator)


cells = [
    Cell.from_file(Path(r"data\components\cells\sony_VTC6.json")),
    Cell.from_file(Path(r"data\components\cells\molicel_P30b.json")),
]

_, axs = plt.subplots(ncols=2)

for cell, ax in zip(cells, axs, strict=True):
    _plot_resistance(cell, ax, title=cell.print_name, y_limits=(0, 30))

plt.show()
