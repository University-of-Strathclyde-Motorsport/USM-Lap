"""
Functions for testing loading vehicles from JSON files.
"""

from pathlib import Path

from usmlap.vehicle.vehicle import Vehicle

VEHICLE = Path(r"data\vehicles\USM26.json")

vehicle = Vehicle.from_json(VEHICLE)
print(vehicle)
