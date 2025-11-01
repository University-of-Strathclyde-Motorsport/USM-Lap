"""
This module defines the interface for vehicle models.
"""

from abc import ABC, abstractmethod
from vehicle.vehicle import Vehicle
from track.mesh import Node
from pydantic import BaseModel


class VehicleState(BaseModel):
    """
    The state of the vehicle at a point.
    """

    velocity: float
    ax: float


class VehicleModelInterface(ABC):
    """
    Abstract base class for vehicle models.
    """

    vehicle: Vehicle

    @abstractmethod
    def lateral_vehicle_model(self, node: Node) -> VehicleState:
        pass

    @abstractmethod
    def calculate_acceleration(self, node: Node, velocity: float) -> float:
        pass

    @abstractmethod
    def calculate_braking(self, node: Node, velocity: float) -> float:
        pass
