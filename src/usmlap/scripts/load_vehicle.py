"""
Functions for testing loading vehicles from JSON files.
"""

from usmlap.vehicle.vehicle import load_vehicle

VEHICLE = "USM23 Baseline.json"


vehicle = load_vehicle(VEHICLE)
print(vehicle)
