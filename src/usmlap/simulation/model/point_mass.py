"""
This module defines the point mass vehicle model.
"""

from .vehicle_model import VehicleModelInterface


class PointMassVehicleModel(VehicleModelInterface):
    """
    Point mass vehicle model.
    """

    def do_something(self) -> None:
        print("hey!")
        return None
