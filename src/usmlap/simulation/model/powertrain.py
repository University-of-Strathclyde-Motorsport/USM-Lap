"""
This module defines the powertrain model.
"""

from abc import ABC, abstractmethod

from .context import Context


class PowertrainModelInterface(ABC):
    """
    Abstract base class for powertrain models.
    """

    @abstractmethod
    def drive_force(self, ctx: Context, velocity: float) -> float: ...


class SingleMotorPowertrain(PowertrainModelInterface):
    """
    Powertrain model for a single-motor vehicle.
    """

    def drive_force(self, ctx: Context, velocity: float) -> float:

        motor_speed = ctx.vehicle.velocity_to_motor_speed(velocity)
        motor_torque = ctx.vehicle.powertrain.get_motor_torque(
            state_of_charge=ctx.state.state_of_charge, motor_speed=motor_speed
        )
        drive_force = ctx.vehicle.motor_torque_to_drive_force(motor_torque)

        return drive_force
