"""
This module defines the powertrain model.
"""

from abc import ABC, abstractmethod

from usmlap.simulation.vehicle_state import StateVariables
from usmlap.vehicle import Vehicle


class PowertrainModelInterface(ABC):
    """
    Abstract base class for powertrain models.
    """

    @abstractmethod
    def drive_force(
        self, vehicle: Vehicle, state: StateVariables, velocity: float
    ) -> float: ...


class SingleMotorPowertrain(PowertrainModelInterface):
    """
    Powertrain model for a single-motor vehicle.
    """

    def drive_force(
        self, vehicle: Vehicle, state: StateVariables, velocity: float
    ) -> float:

        motor_speed = vehicle.velocity_to_motor_speed(velocity)
        motor_torque = vehicle.powertrain.get_motor_torque(
            state_of_charge=state.state_of_charge, motor_speed=motor_speed
        )
        drive_force = vehicle.motor_torque_to_drive_force(motor_torque)

        return drive_force
