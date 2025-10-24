"""
This module defines the interface for vehicle models.
"""

from abc import ABC, abstractmethod
from vehicle.vehicle import Vehicle
from simulation.environment import Environment
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

    @abstractmethod
    def lateral_vehicle_model(
        self, vehicle: Vehicle, environment: Environment, node: Node
    ) -> VehicleState:
        pass

    @abstractmethod
    def calculate_acceleration(
        self,
        vehicle: Vehicle,
        environment: Environment,
        node: Node,
        velocity: float,
    ) -> float:
        pass

    @abstractmethod
    def calculate_braking(
        self,
        vehicle: Vehicle,
        environment: Environment,
        node: Node,
        velocity: float,
    ) -> float:
        pass
