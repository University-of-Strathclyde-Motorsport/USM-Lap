"""
Functions for testing loading vehicles from JSON files.
"""

from usmlap.vehicle import Vehicle

VEHICLE = "USM23 Baseline"

vehicle = Vehicle.from_json(VEHICLE)
print(vehicle)
