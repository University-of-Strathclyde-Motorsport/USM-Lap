"""
Main entry point for the program.
"""

import logging

from usmlap.vehicle.powertrain import Accumulator, Cell

CHANNELS = [
    "Velocity",
    "Curvature",
    "Longitudinal Acceleration",
    "Lateral Acceleration",
    "State of Charge",
]

logging.basicConfig(
    level=logging.WARN,
    format="{asctime} {levelname}: {message}",
    style="{",
    datefmt="%H:%M:%S",
)
logging.getLogger("simulation.model.point_mass").setLevel(logging.DEBUG)

items = Cell.list_items()
print(items)

print(Cell.item_exists("Test Cell"))

cell = Cell.get_item("molicel_P30b")
print(cell)

accus = Accumulator.list_items()
print(accus)

cell_library = Cell.library()
for key, value in cell_library.items():
    print(f"{key}: {value}")

accumulator_library = Accumulator.library()
print(accumulator_library)
